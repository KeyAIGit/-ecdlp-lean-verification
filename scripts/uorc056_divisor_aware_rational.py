#!/usr/bin/env python3
"""Exact divisor-aware rational-character screen for UORC-056.

The profile admits ratios of public affine line functions. Numerator and
denominator zeros may cancel only when their local orders agree at every tested
subgroup point. The regularized value is computed from exact local-series
leading coefficients. No external point, scalar, wallet or production target
is accepted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import uorc056_circuit_synth as base

Curve = tuple[int, int, tuple[int, int]]
Line = tuple[str, str, str]
LocalPoint = tuple[int, int, int, int, int]
Context = tuple[Curve, tuple[LocalPoint, ...], int]


@dataclass(frozen=True)
class LineProfile:
    orders: tuple[int, ...]
    leads: tuple[tuple[int, int], ...]
    zero_count: int


@dataclass(frozen=True)
class RatioMeta:
    numerator: Line
    denominator: Line
    canceled_orbit_zero: bool
    canceled_point_count: int


def is_prime(value: int) -> bool:
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
        raise AssertionError("expected exactly two nontrivial cube roots")
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
        raise AssertionError(f"unknown public coefficient symbol: {name}")
    return values[name] % p


def local_y_series(point: tuple[int, int], p: int) -> LocalPoint:
    """Return x0,y0,d1,d2,d3 for y(x0+t) modulo t^4."""
    x, y = point
    if y % p == 0:
        raise AssertionError("x-x(P) is not a uniformizer at a 2-torsion point")
    inv_2y = pow((2 * y) % p, -1, p)
    d1 = 3 * x * x * inv_2y % p
    d2 = (3 * x - d1 * d1) * inv_2y % p
    d3 = (1 - 2 * d1 * d2) * inv_2y % p

    if (2 * y * d1 - 3 * x * x) % p:
        raise AssertionError("first local-series coefficient drifted")
    if (d1 * d1 + 2 * y * d2 - 3 * x) % p:
        raise AssertionError("second local-series coefficient drifted")
    if (2 * y * d3 + 2 * d1 * d2 - 1) % p:
        raise AssertionError("third local-series coefficient drifted")
    return x, y, d1, d2, d3


def contexts(curves: Sequence[Curve]) -> tuple[list[Context], int]:
    result: list[Context] = []
    offset = 0
    for curve in curves:
        p, n, generator = curve
        if not is_prime(p) or not is_prime(n) or p % 3 != 1:
            raise AssertionError("corpus requires prime p,n and p congruent 1 mod 3")
        points = base.orbit(generator, n, p)
        local_points = tuple(
            local_y_series(point, p)
            for point in points[1:]
            if point is not None
        )
        if len(local_points) != n - 1:
            raise AssertionError("frozen orbit unexpectedly contains infinity")
        result.append((curve, local_points, offset))
        offset += n - 1
    return result, offset


def line_templates(grammar: dict) -> list[Line]:
    coefficients = grammar["line_templates"]["linear_coefficients"]
    offsets = grammar["line_templates"]["offsets"]
    lines = [
        (a, b, c)
        for a in coefficients
        for b in coefficients
        if not (a == "zero" and b == "zero")
        for c in offsets
    ]
    expected = grammar["line_templates"]["raw_count"]
    if len(lines) != expected:
        raise AssertionError("line-template count drifted")
    return lines


def line_order_and_lead(
    a: int, b: int, c: int, local_point: LocalPoint, p: int
) -> tuple[int, int]:
    x, y, d1, d2, d3 = local_point
    constant = (a * x + b * y + c) % p
    if constant:
        return 0, constant

    coefficients = (
        (a + b * d1) % p,
        b * d2 % p,
        b * d3 % p,
    )
    for order, coefficient in enumerate(coefficients, start=1):
        if coefficient:
            return order, coefficient

    raise AssertionError(
        "affine line has intersection multiplicity above the cubic Bezout bound"
    )


def line_profile(line: Line, curve_contexts: Sequence[Context]) -> LineProfile:
    orders: list[int] = []
    leads: list[tuple[int, int]] = []
    zero_count = 0
    for curve, local_points, _ in curve_contexts:
        p, _, _ = curve
        a = symbol(line[0], curve)
        b = symbol(line[1], curve)
        c = symbol(line[2], curve)
        if a == 0 and b == 0:
            raise AssertionError("symbolic nonzero line specialized to a constant")
        for local_point in local_points:
            order, lead = line_order_and_lead(a, b, c, local_point, p)
            orders.append(order)
            leads.append((lead, p))
            zero_count += int(order > 0)
    return LineProfile(tuple(orders), tuple(leads), zero_count)


def ratio_sign_bits(
    numerator: Line,
    denominator: Line,
    profiles: dict[Line, LineProfile],
) -> int:
    numerator_profile = profiles[numerator]
    denominator_profile = profiles[denominator]
    if numerator_profile.orders != denominator_profile.orders:
        raise AssertionError("ratio has an uncanceled zero or pole on the orbit")

    bits = 0
    for index, ((num_lead, p), (den_lead, den_p)) in enumerate(
        zip(numerator_profile.leads, denominator_profile.leads)
    ):
        if p != den_p or num_lead == 0 or den_lead == 0:
            raise AssertionError("invalid regularized leading coefficient")
        regular_value = num_lead * pow(den_lead, -1, p) % p
        sign = base.chi(regular_value, p)
        if sign == -1:
            bits |= 1 << index
    return bits


def ratio_json(meta: RatioMeta) -> dict:
    def line_json(line: Line) -> dict:
        return {"a": line[0], "b": line[1], "c": line[2]}

    return {
        "numerator": line_json(meta.numerator),
        "denominator": line_json(meta.denominator),
        "canceled_orbit_zero": meta.canceled_orbit_zero,
        "canceled_point_count": meta.canceled_point_count,
    }


def rational_catalog(
    lines: Sequence[Line], curve_contexts: Sequence[Context]
) -> tuple[dict[int, RatioMeta], dict]:
    profiles = {line: line_profile(line, curve_contexts) for line in lines}
    valuation_classes: dict[tuple[int, ...], list[Line]] = defaultdict(list)
    for line, profile in profiles.items():
        valuation_classes[profile.orders].append(line)

    representatives: dict[int, RatioMeta] = {}
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
                bits = ratio_sign_bits(numerator, denominator, profiles)
                meta = RatioMeta(
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
        "valuation_signatures": len(valuation_classes),
        "admissible_unordered_ratios": admissible_ratios,
        "ratios_with_canceled_orbit_zero": exceptional_ratios,
        "unique_sign_vectors": len(representatives),
        "nonexceptional_sign_vectors": len(nonexceptional_vectors),
        "unique_exceptional_sign_vectors": len(exceptional_vectors),
        "novel_exceptional_sign_vectors": len(
            exceptional_vectors - nonexceptional_vectors
        ),
    }
    return representatives, stats


def target_bits(curve_contexts: Sequence[Context]) -> int:
    result = 0
    for (_, n, _), _, offset in curve_contexts:
        result |= base.parity_bits(n) << offset
    return result


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
    representatives: dict[int, RatioMeta],
    vectors: Sequence[int],
    indices: tuple[int, ...],
    phase: int,
) -> dict:
    return {
        "weight": len(indices),
        "output_phase": phase,
        "atoms": [ratio_json(representatives[vectors[index]]) for index in indices],
    }


def exact_search(
    representatives: dict[int, RatioMeta],
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
    representatives: dict[int, RatioMeta], target: int, total: int
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
            "atoms": [ratio_json(representatives[vectors[single_index]])],
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


def run(grammar_path: Path) -> dict:
    grammar_bytes = grammar_path.read_bytes()
    grammar = json.loads(grammar_bytes)
    if grammar["profile_id"] != "UORC-056-DIVISOR-AWARE-LINE-RATIO-V1":
        raise AssertionError("unexpected rational grammar")

    discovery_curves = tuple(
        parse_curve(row) for row in grammar["discovery_corpus"]
    )
    holdout_curves = tuple(parse_curve(row) for row in grammar["holdout_corpus"])
    discovery_contexts, discovery_total = contexts(discovery_curves)
    full_contexts, full_total = contexts(discovery_curves + holdout_curves)
    lines = line_templates(grammar)

    discovery_representatives, discovery_stats = rational_catalog(
        lines, discovery_contexts
    )
    full_representatives, full_stats = rational_catalog(lines, full_contexts)
    maximum_weight = grammar["sign_circuit"]["maximum_weight"]
    discovery_target = target_bits(discovery_contexts)
    full_target = target_bits(full_contexts)
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
        decision = "no_exact_divisor_aware_line_ratio_circuit_weight_le_4"
    elif full_candidate is None:
        transfer_status = "discovery_candidate_failed_full_corpus"
        decision = "finite_discovery_only_rational_candidate"
    else:
        transfer_status = "full_corpus_candidate_requires_symbolic_proof"
        decision = "symbolic_followup_required"

    return {
        "schema_version": "1.0",
        "experiment": "UORC-056-DIVISOR-AWARE-LINE-RATIO-V1",
        "grammar_sha256": hashlib.sha256(grammar_bytes).hexdigest(),
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
            "six discovery-only semantic vectors are introduced by removable "
            "line-ratio singularities, but zero remain novel on the full corpus"
        ),
        "transfer_status": transfer_status,
        "decision": decision,
        "claim_boundary": [
            "This is complete only for ratios of the declared affine line templates and products of at most four character atoms.",
            "It does not cover ratios of higher-degree functions, pullbacks through index-growing maps, EDS factors or unrestricted straight-line programs.",
            "Local values are derived from exact series coefficients; no exceptional point is patched or omitted.",
            "No external point, wallet, real key or production-sized discrete-log target is accepted.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--grammar",
        type=Path,
        default=Path("experiments/uorc056/divisor_aware_rational_grammar.json"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("experiments/uorc056/divisor_aware_rational_results.json"),
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = json.dumps(run(args.grammar), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("divisor-aware rational result drift")
        print("UORC056_DIVISOR_AWARE_RATIONAL_OK")
        return 0
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
