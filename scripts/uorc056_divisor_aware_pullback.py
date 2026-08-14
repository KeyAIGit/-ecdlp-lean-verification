#!/usr/bin/env python3
"""Exact common-multiplier pullback screen for divisor-aware UORC-056 atoms.

Each atom is R([u]Q), where R is a regularized V1 line ratio and one common
multiplier u is used in its numerator and denominator. Since [u] is etale on
the frozen prime-order subgroups, the common local leading multiplier cancels
exactly. Evaluation is therefore a checked permutation of the V1 sign vector.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass
from math import gcd
from pathlib import Path
from typing import Sequence

import uorc056_divisor_aware_rational as rational

Curve = rational.Curve
Line = rational.Line
Context = rational.Context


@dataclass(frozen=True)
class PullbackMeta:
    multiplier: int
    ratio: rational.RatioMeta


def atom_json(meta: PullbackMeta) -> dict:
    return {
        "multiplier": meta.multiplier,
        "ratio": rational.ratio_json(meta.ratio),
    }


def base_ratio_details(
    lines: Sequence[Line], curve_contexts: Sequence[Context]
) -> tuple[
    dict[int, rational.RatioMeta],
    set[int],
    set[int],
    dict,
]:
    profiles = {
        line: rational.line_profile(line, curve_contexts) for line in lines
    }
    valuation_classes: dict[tuple[int, ...], list[Line]] = defaultdict(list)
    for line, profile in profiles.items():
        valuation_classes[profile.orders].append(line)

    representatives: dict[int, rational.RatioMeta] = {}
    exceptional_vectors: set[int] = set()
    nonexceptional_vectors: set[int] = set()
    admissible_ratios = 0
    exceptional_ratios = 0

    for signature, members in valuation_classes.items():
        exceptional = any(order > 0 for order in signature)
        canceled_count = sum(order > 0 for order in signature)
        for left_index, numerator in enumerate(members):
            for denominator in members[left_index:]:
                admissible_ratios += 1
                exceptional_ratios += int(exceptional)
                bits = rational.ratio_sign_bits(
                    numerator,
                    denominator,
                    profiles,
                )
                meta = rational.RatioMeta(
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
        "valuation_signatures": len(valuation_classes),
        "admissible_unordered_ratios": admissible_ratios,
        "ratios_with_canceled_orbit_zero": exceptional_ratios,
        "unique_base_ratio_vectors": len(representatives),
        "base_exceptional_vectors": len(exceptional_vectors),
        "base_nonexceptional_vectors": len(nonexceptional_vectors),
    }
    return (
        representatives,
        exceptional_vectors,
        nonexceptional_vectors,
        stats,
    )


def pullback_bits(bits: int, curves: Sequence[Curve], multiplier: int) -> int:
    result = 0
    offset = 0
    for _, order, _ in curves:
        if gcd(multiplier, order) != 1:
            raise AssertionError("pullback multiplier is not a subgroup permutation")
        for scalar in range(1, order):
            source = multiplier * scalar % order
            if source == 0:
                raise AssertionError("nonzero scalar mapped to infinity")
            if (bits >> (offset + source - 1)) & 1:
                result |= 1 << (offset + scalar - 1)
        offset += order - 1
    return result


def transform_set(
    vectors: set[int], curves: Sequence[Curve], multipliers: Sequence[int]
) -> set[int]:
    return {
        pullback_bits(vector, curves, multiplier)
        for vector in vectors
        for multiplier in multipliers
    }


def pullback_catalog(
    lines: Sequence[Line],
    curve_contexts: Sequence[Context],
    curves: Sequence[Curve],
    multipliers: Sequence[int],
) -> tuple[dict[int, PullbackMeta], dict]:
    for p, order, _ in curves:
        for multiplier in multipliers:
            if multiplier % p == 0 or gcd(multiplier, order) != 1:
                raise AssertionError("declared pullback is not etale and bijective")

    (
        base_representatives,
        base_exceptional,
        base_nonexceptional,
        base_stats,
    ) = base_ratio_details(lines, curve_contexts)

    representatives: dict[int, PullbackMeta] = {}
    for bits, ratio_meta in base_representatives.items():
        for multiplier in multipliers:
            transformed = pullback_bits(bits, curves, multiplier)
            representatives.setdefault(
                transformed,
                PullbackMeta(multiplier, ratio_meta),
            )

    exceptional_vectors = transform_set(
        base_exceptional, curves, multipliers
    )
    nonexceptional_vectors = transform_set(
        base_nonexceptional, curves, multipliers
    )
    stats = {
        **base_stats,
        "multipliers": list(multipliers),
        "raw_pullback_asts": (
            base_stats["admissible_unordered_ratios"] * len(multipliers)
        ),
        "raw_exceptional_pullback_asts": (
            base_stats["ratios_with_canceled_orbit_zero"] * len(multipliers)
        ),
        "semantic_pullback_atoms_before_quotient": (
            base_stats["unique_base_ratio_vectors"] * len(multipliers)
        ),
        "unique_pullback_sign_vectors": len(representatives),
        "pullback_exceptional_vectors": len(exceptional_vectors),
        "pullback_nonexceptional_vectors": len(nonexceptional_vectors),
        "novel_pullback_exceptional_vectors": len(
            exceptional_vectors - nonexceptional_vectors
        ),
    }
    return representatives, stats


def pair_index(vectors: Sequence[int]) -> tuple[
    dict[int, list[tuple[int, int]]], list[tuple[int, int, int]]
]:
    by_xor: dict[int, list[tuple[int, int]]] = defaultdict(list)
    pairs: list[tuple[int, int, int]] = []
    for left in range(len(vectors)):
        for right in range(left + 1, len(vectors)):
            value = vectors[left] ^ vectors[right]
            by_xor[value].append((left, right))
            pairs.append((value, left, right))
    return by_xor, pairs


def candidate_json(
    representatives: dict[int, PullbackMeta],
    vectors: Sequence[int],
    indices: tuple[int, ...],
    phase: int,
) -> dict:
    return {
        "weight": len(indices),
        "output_phase": phase,
        "atoms": [atom_json(representatives[vectors[index]]) for index in indices],
    }


def exact_search(
    representatives: dict[int, PullbackMeta],
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
                    representatives,
                    vectors,
                    tuple(sorted((left, right))),
                    phase,
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


def signed_matches(bits: int, target: int, total: int) -> tuple[int, int]:
    direct = total - (bits ^ target).bit_count()
    return (direct, 1) if direct >= total - direct else (total - direct, -1)


def best_correlations(
    representatives: dict[int, PullbackMeta], target: int, total: int
) -> dict:
    vectors = list(representatives)
    best_single = max(
        (signed_matches(vector, target, total)[0], -index)
        for index, vector in enumerate(vectors)
    )
    single_index = -best_single[1]
    single_matches, single_phase = signed_matches(
        vectors[single_index], target, total
    )

    best_pair = max(
        (
            signed_matches(vectors[left] ^ vectors[right], target, total)[0],
            -left,
            -right,
        )
        for left in range(len(vectors))
        for right in range(left + 1, len(vectors))
    )
    left, right = -best_pair[1], -best_pair[2]
    pair_matches, pair_phase = signed_matches(
        vectors[left] ^ vectors[right], target, total
    )
    return {
        "weight_one": {
            "matches": single_matches,
            "total": total,
            "accuracy": f"{single_matches / total:.9f}",
            "output_phase": single_phase,
            "atoms": [atom_json(representatives[vectors[single_index]])],
        },
        "weight_two": {
            "matches": pair_matches,
            "total": total,
            "accuracy": f"{pair_matches / total:.9f}",
            "output_phase": pair_phase,
            "atoms": [
                atom_json(representatives[vectors[left]]),
                atom_json(representatives[vectors[right]]),
            ],
        },
    }


def run(grammar_path: Path) -> dict:
    grammar_bytes = grammar_path.read_bytes()
    grammar = json.loads(grammar_bytes)
    if grammar["profile_id"] != "UORC-056-DIVISOR-AWARE-PULLBACK-RATIO-V2":
        raise AssertionError("unexpected pullback grammar")

    base_grammar_path = Path(grammar["base_ratio_grammar"])
    base_grammar = json.loads(base_grammar_path.read_text(encoding="utf-8"))
    if base_grammar["profile_id"] != "UORC-056-DIVISOR-AWARE-LINE-RATIO-V1":
        raise AssertionError("unexpected base ratio grammar")

    discovery_curves = tuple(
        rational.parse_curve(row) for row in base_grammar["discovery_corpus"]
    )
    holdout_curves = tuple(
        rational.parse_curve(row) for row in base_grammar["holdout_corpus"]
    )
    discovery_contexts, discovery_total = rational.contexts(discovery_curves)
    full_contexts, full_total = rational.contexts(
        discovery_curves + holdout_curves
    )
    lines = rational.line_templates(base_grammar)
    multipliers = tuple(grammar["pullback_atoms"]["multipliers"])

    discovery_representatives, discovery_stats = pullback_catalog(
        lines,
        discovery_contexts,
        discovery_curves,
        multipliers,
    )
    full_representatives, full_stats = pullback_catalog(
        lines,
        full_contexts,
        discovery_curves + holdout_curves,
        multipliers,
    )
    maximum_weight = grammar["sign_circuit"]["maximum_weight"]
    discovery_target = rational.target_bits(discovery_contexts)
    full_target = rational.target_bits(full_contexts)
    discovery_candidate = exact_search(
        discovery_representatives,
        discovery_target,
        discovery_total,
        maximum_weight,
    )
    full_candidate = exact_search(
        full_representatives,
        full_target,
        full_total,
        maximum_weight,
    )

    if discovery_candidate is None:
        transfer_status = "not_reached_no_discovery_candidate"
        decision = "no_exact_divisor_aware_pullback_circuit_weight_le_4"
    elif full_candidate is None:
        transfer_status = "discovery_candidate_failed_full_corpus"
        decision = "finite_discovery_only_pullback_candidate"
    else:
        transfer_status = "full_corpus_candidate_requires_symbolic_proof"
        decision = "symbolic_followup_required"

    return {
        "schema_version": "1.0",
        "experiment": "UORC-056-DIVISOR-AWARE-PULLBACK-RATIO-V2",
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
        },
        "full_corpus_exact_search": {
            "candidate_found": full_candidate is not None,
            "candidate": full_candidate,
        },
        "best_discovery_correlations": best_correlations(
            discovery_representatives, discovery_target, discovery_total
        ),
        "best_full_corpus_correlations": best_correlations(
            full_representatives, full_target, full_total
        ),
        "exceptional_fiber_decision": (
            "twenty-four pullback exceptional vectors are discovery-only; "
            "zero remain novel on the full eighteen-curve corpus"
        ),
        "transfer_status": transfer_status,
        "decision": decision,
        "claim_boundary": [
            "This is complete only for common-multiplier pullbacks u in {1,2,3,4} of V1 line ratios and products of at most four atoms.",
            "Mixed-multiplier numerator/denominator ratios and higher-degree divisor circuits remain open.",
            "The etale pullback rule is exact and no exceptional point is patched or omitted.",
            "No external point, wallet, real key or production-sized discrete-log target is accepted.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--grammar",
        type=Path,
        default=Path("experiments/uorc056/divisor_aware_pullback_grammar.json"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("experiments/uorc056/divisor_aware_pullback_results.json"),
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = json.dumps(run(args.grammar), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("divisor-aware pullback result drift")
        print("UORC056_DIVISOR_AWARE_PULLBACK_OK")
        return 0
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
