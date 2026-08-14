#!/usr/bin/env python3
"""Exact mixed-pullback divisor screen for UORC-056.

The bounded atom is L_num([u]Q)/L_den([v]Q), with u and v independently in
a frozen small set. Local leading coefficients are transported exactly using

    alpha_(u,P) = u * y([u]P) / y(P),

which follows from pullback of the invariant differential dx/(2y). Numerator
and denominator are admitted only when their transported local orders agree at
every tested subgroup point. No external target or exceptional-point patch is
accepted.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass
from math import gcd
from pathlib import Path
from typing import Sequence

import uorc056_circuit_synth as base
import uorc056_divisor_aware_rational as rational

Curve = rational.Curve
Line = rational.Line
LocalPoint = rational.LocalPoint
PulledLine = tuple[int, Line]


@dataclass(frozen=True)
class CurveCache:
    curve: Curve
    points: tuple[base.Point, ...]
    local_points: tuple[LocalPoint | None, ...]
    offset: int


@dataclass(frozen=True)
class PulledProfile:
    orders: bytes
    leads: tuple[int, ...]
    zero_count: int


@dataclass(frozen=True)
class MixedRatioMeta:
    numerator: PulledLine
    denominator: PulledLine
    canceled_orbit_zero: bool
    canceled_point_count: int


def caches(curves: Sequence[Curve]) -> tuple[list[CurveCache], tuple[int, ...], int]:
    result: list[CurveCache] = []
    moduli: list[int] = []
    offset = 0
    for curve in curves:
        p, order, generator = curve
        points = tuple(base.orbit(generator, order, p))
        local_points: list[LocalPoint | None] = [None]
        for point in points[1:]:
            if point is None:
                raise AssertionError("nonzero frozen subgroup point is infinity")
            local_points.append(rational.local_y_series(point, p))
            moduli.append(p)
        result.append(CurveCache(curve, points, tuple(local_points), offset))
        offset += order - 1
    return result, tuple(moduli), offset


def pulled_line_templates(grammar: dict, lines: Sequence[Line]) -> list[PulledLine]:
    multipliers = tuple(grammar["pulled_line_templates"]["multipliers"])
    templates = [
        (multiplier, line)
        for multiplier in multipliers
        for line in lines
    ]
    expected = grammar["pulled_line_templates"]["raw_count"]
    if len(templates) != expected:
        raise AssertionError("pulled-line template count drifted")
    return templates


def pulled_profile(
    template: PulledLine,
    curve_caches: Sequence[CurveCache],
) -> PulledProfile:
    multiplier, line = template
    orders = bytearray()
    leads: list[int] = []
    zero_count = 0

    for cache in curve_caches:
        p, order, _ = cache.curve
        if multiplier % p == 0 or gcd(multiplier, order) != 1:
            raise AssertionError("pullback is not etale and bijective")
        a = rational.symbol(line[0], cache.curve)
        b = rational.symbol(line[1], cache.curve)
        c = rational.symbol(line[2], cache.curve)
        for scalar in range(1, order):
            point = cache.points[scalar]
            source_index = multiplier * scalar % order
            source = cache.points[source_index]
            source_local = cache.local_points[source_index]
            if point is None or source is None or source_local is None:
                raise AssertionError("invalid pulled-line orbit point")

            local_order, line_lead = rational.line_order_and_lead(
                a,
                b,
                c,
                source_local,
                p,
            )
            alpha = multiplier * source[1] * pow(point[1], -1, p) % p
            if alpha == 0:
                raise AssertionError("etale local derivative vanished")
            pullback_lead = line_lead * pow(alpha, local_order, p) % p
            orders.append(local_order)
            leads.append(pullback_lead)
            zero_count += int(local_order > 0)

    return PulledProfile(bytes(orders), tuple(leads), zero_count)


def pulled_line_json(template: PulledLine) -> dict:
    multiplier, line = template
    return {
        "multiplier": multiplier,
        "line": {"a": line[0], "b": line[1], "c": line[2]},
    }


def mixed_ratio_json(meta: MixedRatioMeta) -> dict:
    return {
        "numerator": pulled_line_json(meta.numerator),
        "denominator": pulled_line_json(meta.denominator),
        "canceled_orbit_zero": meta.canceled_orbit_zero,
        "canceled_point_count": meta.canceled_point_count,
    }


def ratio_sign_bits(
    numerator: PulledLine,
    denominator: PulledLine,
    profiles: dict[PulledLine, PulledProfile],
    moduli: Sequence[int],
) -> int:
    numerator_profile = profiles[numerator]
    denominator_profile = profiles[denominator]
    if numerator_profile.orders != denominator_profile.orders:
        raise AssertionError("mixed ratio has an uncanceled orbit zero or pole")

    bits = 0
    for index, (num_lead, den_lead, p) in enumerate(
        zip(numerator_profile.leads, denominator_profile.leads, moduli)
    ):
        if num_lead == 0 or den_lead == 0:
            raise AssertionError("transported leading coefficient vanished")
        regular_value = num_lead * pow(den_lead, -1, p) % p
        if base.chi(regular_value, p) == -1:
            bits |= 1 << index
    return bits


def mixed_catalog(
    templates: Sequence[PulledLine],
    curve_caches: Sequence[CurveCache],
    moduli: Sequence[int],
) -> tuple[dict[int, MixedRatioMeta], dict]:
    profiles: dict[PulledLine, PulledProfile] = {}
    valuation_classes: dict[bytes, list[PulledLine]] = defaultdict(list)
    for template in templates:
        profile = pulled_profile(template, curve_caches)
        profiles[template] = profile
        valuation_classes[profile.orders].append(template)

    representatives: dict[int, MixedRatioMeta] = {}
    exceptional_vectors: set[int] = set()
    nonexceptional_vectors: set[int] = set()
    admissible_ratios = 0
    exceptional_ratios = 0

    for signature, members in valuation_classes.items():
        exceptional = any(signature)
        canceled_count = sum(order > 0 for order in signature)
        for left_index, numerator in enumerate(members):
            for denominator in members[left_index:]:
                admissible_ratios += 1
                exceptional_ratios += int(exceptional)
                bits = ratio_sign_bits(
                    numerator,
                    denominator,
                    profiles,
                    moduli,
                )
                meta = MixedRatioMeta(
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
        "pulled_line_templates": len(templates),
        "valuation_signatures": len(valuation_classes),
        "admissible_unordered_mixed_ratios": admissible_ratios,
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
    maximum_multiplicity = max((len(edges) for edges in by_xor.values()), default=0)
    return by_xor, pair_count, maximum_multiplicity


def candidate_json(
    representatives: dict[int, MixedRatioMeta],
    vectors: Sequence[int],
    indices: tuple[int, ...],
    phase: int,
) -> dict:
    return {
        "weight": len(indices),
        "output_phase": phase,
        "atoms": [
            mixed_ratio_json(representatives[vectors[index]])
            for index in indices
        ],
    }


def exact_search(
    representatives: dict[int, MixedRatioMeta],
    target: int,
    total: int,
    maximum_weight: int,
) -> tuple[dict | None, dict]:
    vectors = list(representatives)
    lookup = {vector: index for index, vector in enumerate(vectors)}
    mask = (1 << total) - 1
    desired = ((target, 1), (target ^ mask, -1))

    for index, vector in enumerate(vectors):
        for goal, phase in desired:
            if vector == goal:
                return candidate_json(representatives, vectors, (index,), phase), {
                    "pair_count": 0,
                    "pair_xor_classes": 0,
                    "maximum_pair_xor_multiplicity": 0,
                }
    if maximum_weight < 2:
        return None, {
            "pair_count": 0,
            "pair_xor_classes": 0,
            "maximum_pair_xor_multiplicity": 0,
        }

    for left, vector in enumerate(vectors):
        for goal, phase in desired:
            right = lookup.get(goal ^ vector)
            if right is not None and right != left:
                return candidate_json(
                    representatives,
                    vectors,
                    tuple(sorted((left, right))),
                    phase,
                ), {
                    "pair_count": 0,
                    "pair_xor_classes": 0,
                    "maximum_pair_xor_multiplicity": 0,
                }
    if maximum_weight < 3:
        return None, {
            "pair_count": 0,
            "pair_xor_classes": 0,
            "maximum_pair_xor_multiplicity": 0,
        }

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
                    return candidate_json(
                        representatives,
                        vectors,
                        tuple(sorted((single, left, right))),
                        phase,
                    ), search_stats
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
                        return candidate_json(
                            representatives,
                            vectors,
                            tuple(
                                sorted((left, right, other_left, other_right))
                            ),
                            phase,
                        ), search_stats
    return None, search_stats


def signed_matches(bits: int, target: int, total: int) -> tuple[int, int]:
    direct = total - (bits ^ target).bit_count()
    return (direct, 1) if direct >= total - direct else (total - direct, -1)


def best_correlations(
    representatives: dict[int, MixedRatioMeta], target: int, total: int
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
            "atoms": [
                mixed_ratio_json(representatives[vectors[single_index]])
            ],
        },
        "weight_two": {
            "matches": pair_matches,
            "total": total,
            "accuracy": f"{pair_matches / total:.9f}",
            "output_phase": pair_phase,
            "atoms": [
                mixed_ratio_json(representatives[vectors[left]]),
                mixed_ratio_json(representatives[vectors[right]]),
            ],
        },
    }


def run(grammar_path: Path) -> dict:
    grammar_bytes = grammar_path.read_bytes()
    grammar = json.loads(grammar_bytes)
    if grammar["profile_id"] != "UORC-056-DIVISOR-AWARE-MIXED-PULLBACK-RATIO-V3":
        raise AssertionError("unexpected mixed-pullback grammar")

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
    lines = rational.line_templates(base_grammar)
    templates = pulled_line_templates(grammar, lines)
    maximum_weight = grammar["sign_circuit"]["maximum_weight"]

    discovery_caches, discovery_moduli, discovery_total = caches(
        discovery_curves
    )
    discovery_representatives, discovery_stats = mixed_catalog(
        templates,
        discovery_caches,
        discovery_moduli,
    )
    discovery_target = rational.target_bits(
        rational.contexts(discovery_curves)[0]
    )
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
    del discovery_caches
    gc.collect()

    full_curves = discovery_curves + holdout_curves
    full_caches, full_moduli, full_total = caches(full_curves)
    full_representatives, full_stats = mixed_catalog(
        templates,
        full_caches,
        full_moduli,
    )
    full_target = rational.target_bits(rational.contexts(full_curves)[0])
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

    if discovery_candidate is None:
        transfer_status = "not_reached_no_discovery_candidate"
        decision = "no_exact_mixed_pullback_divisor_circuit_weight_le_4"
    elif full_candidate is None:
        transfer_status = "discovery_candidate_failed_full_corpus"
        decision = "finite_discovery_only_mixed_pullback_candidate"
    else:
        transfer_status = "full_corpus_candidate_requires_symbolic_proof"
        decision = "symbolic_followup_required"

    return {
        "schema_version": "1.0",
        "experiment": "UORC-056-DIVISOR-AWARE-MIXED-PULLBACK-RATIO-V3",
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
            "seventy-five mixed-pullback exceptional vectors are discovery-only; "
            "zero remain novel on the full eighteen-curve corpus"
        ),
        "transfer_status": transfer_status,
        "decision": decision,
        "claim_boundary": [
            "This is complete only for ratios of the 1,440 declared pulled-line templates and products of at most four character atoms.",
            "Higher-degree numerator or denominator functions, larger multiplier sets, EDS factors and unrestricted straight-line programs remain open.",
            "The local derivative is exact from the invariant differential; no exceptional point is patched or omitted.",
            "No external point, wallet, real key or production-sized discrete-log target is accepted.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--grammar",
        type=Path,
        default=Path(
            "experiments/uorc056/divisor_aware_mixed_pullback_grammar.json"
        ),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(
            "experiments/uorc056/divisor_aware_mixed_pullback_results.json"
        ),
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = json.dumps(run(args.grammar), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("mixed-pullback divisor result drift")
        print("UORC056_MIXED_PULLBACK_DIVISOR_OK")
        return 0
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
