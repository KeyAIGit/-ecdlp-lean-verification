#!/usr/bin/env python3
"""Screen globally balanced 2-by-2 pulled-line character circuits on frozen toys."""
from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from uorc056_divisor_common import (
    CurveData,
    SparseValuation,
    add_sparse,
    build_discovery_corpus,
    pulled_line_local_data,
    quadratic_character,
    stable_json,
)

MULTIPLIERS = (1, 2, 3, 4)
LINEAR_LABELS = ("zero", "one", "neg_one", "beta_lo", "beta_hi")
OFFSET_LABELS = (
    "zero", "one", "neg_one", "two", "neg_two", "curve_b", "neg_curve_b",
    "x_G", "neg_x_G", "y_G", "neg_y_G", "beta_lo", "beta_hi",
    "x_G_plus_y_G", "x_G_minus_y_G",
)


@dataclass(frozen=True, order=True)
class LineTemplate:
    a: str
    b: str
    c: str
    multiplier: int


@dataclass(frozen=True)
class LocalSemantics:
    valuation: SparseValuation
    sign_bits: int
    representative: LineTemplate
    multiplicity: int = 1


def line_templates() -> Iterator[LineTemplate]:
    for multiplier in MULTIPLIERS:
        for a in LINEAR_LABELS:
            for b in LINEAR_LABELS:
                if a == "zero" and b == "zero":
                    continue
                for c in OFFSET_LABELS:
                    yield LineTemplate(a, b, c, multiplier)


def line_tuple(curve: CurveData, template: LineTemplate) -> tuple[int, int, int]:
    table = curve.coefficients
    return table[template.a], table[template.b], table[template.c]


def build_semantics() -> tuple[list[LocalSemantics], int, int, list[dict[str, object]]]:
    curves, target, total, public = build_discovery_corpus()
    quotient: dict[tuple[SparseValuation, int], tuple[LineTemplate, int]] = {}
    for template in line_templates():
        valuation: list[tuple[int, int]] = []
        signs = 0
        for curve in curves:
            line = line_tuple(curve, template)
            for k in range(1, curve.n):
                order, leading = pulled_line_local_data(
                    curve, k, template.multiplier, line
                )
                position = curve.offset + k - 1
                if order:
                    valuation.append((position, order))
                sign = quadratic_character(leading, curve.p)
                if sign == -1:
                    signs |= 1 << position
                elif sign != 1:
                    raise AssertionError("leading coefficient vanished")
        key = (tuple(valuation), signs)
        if key in quotient:
            representative, multiplicity = quotient[key]
            quotient[key] = representative, multiplicity + 1
        else:
            quotient[key] = template, 1
    semantics = [
        LocalSemantics(valuation, signs, representative, multiplicity)
        for (valuation, signs), (representative, multiplicity) in quotient.items()
    ]
    semantics.sort(key=lambda item: (
        item.valuation, item.sign_bits, item.representative
    ))
    return semantics, target, total, public


def template_json(template: LineTemplate) -> dict[str, object]:
    return {
        "multiplier": template.multiplier,
        "line": {"a": template.a, "b": template.b, "c": template.c},
    }


def hamming_matches(bits: int, target: int, total: int) -> tuple[int, int]:
    errors = (bits ^ target).bit_count()
    if errors > total - errors:
        return errors, -1
    return total - errors, 1


def search(
    semantics: list[LocalSemantics], target: int, total: int
) -> dict[str, object]:
    mask = (1 << total) - 1
    complement = target ^ mask
    by_valuation: dict[SparseValuation, list[int]] = {}
    for index, item in enumerate(semantics):
        by_valuation.setdefault(item.valuation, []).append(index)

    best = {"matches": -1}
    balanced_one_by_one = 0
    for indices in by_valuation.values():
        for position, i in enumerate(indices):
            for j in indices[position:]:
                balanced_one_by_one += 1
                bits = semantics[i].sign_bits ^ semantics[j].sign_bits
                matches, phase = hamming_matches(bits, target, total)
                if matches > int(best["matches"]):
                    best = {
                        "matches": matches,
                        "total": total,
                        "accuracy": f"{matches / total:.9f}",
                        "output_phase": phase,
                        "numerator": template_json(semantics[i].representative),
                        "denominator": template_json(semantics[j].representative),
                    }

    buckets: dict[SparseValuation, dict[int, tuple[int, int]]] = {}
    pair_count = unique_states = repeated_states = maximum_bucket = 0
    exact: dict[str, object] | None = None
    for i, left in enumerate(semantics):
        for j in range(i, len(semantics)):
            right = semantics[j]
            pair_count += 1
            divisor = add_sparse(left.valuation, right.valuation)
            sign = left.sign_bits ^ right.sign_bits
            bucket = buckets.setdefault(divisor, {})
            if exact is None:
                other = bucket.get(target ^ sign)
                phase = 1
                if other is None:
                    other = bucket.get(complement ^ sign)
                    phase = -1
                if other is not None:
                    oi, oj = other
                    exact = {
                        "candidate_found": True,
                        "output_phase": phase,
                        "total_line_factors": 4,
                        "numerator": [
                            template_json(left.representative),
                            template_json(right.representative),
                        ],
                        "denominator": [
                            template_json(semantics[oi].representative),
                            template_json(semantics[oj].representative),
                        ],
                    }
            if sign in bucket:
                repeated_states += 1
            else:
                bucket[sign] = i, j
                unique_states += 1
                maximum_bucket = max(maximum_bucket, len(bucket))
    if exact is None:
        exact = {"candidate_found": False, "candidate": None}

    sampled_checks = 0
    for divisor, bucket in list(buckets.items())[:64]:
        for sign, (i, j) in list(bucket.items())[:64]:
            assert add_sparse(semantics[i].valuation, semantics[j].valuation) == divisor
            assert semantics[i].sign_bits ^ semantics[j].sign_bits == sign
            sampled_checks += 1

    return {
        "exact_search": exact,
        "catalog": {
            "semantic_pulled_line_templates": len(semantics),
            "base_valuation_signatures": len(by_valuation),
            "balanced_one_by_one_states_checked": balanced_one_by_one,
            "unordered_template_pairs_checked": pair_count,
            "aggregate_divisor_signatures": len(buckets),
            "unique_pair_semantic_states": unique_states,
            "repeated_pair_semantic_states": repeated_states,
            "maximum_semantic_states_in_one_divisor_bucket": maximum_bucket,
            "sampled_internal_state_checks": sampled_checks,
        },
        "best_balanced_one_by_one_correlation": best,
    }


def grammar_payload() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "profile_id": "UORC-056-GLOBAL-DIVISOR-BALANCE-V4",
        "curve_model": "y^2=x^3+7 over five frozen odd prime-order toy subgroups",
        "pulled_line_templates": {
            "formula": "L([u]Q), L=a*x+b*y+c",
            "multipliers": list(MULTIPLIERS),
            "linear_coefficients": list(LINEAR_LABELS),
            "offsets": list(OFFSET_LABELS),
            "raw_count": 1440,
            "local_parameter": "t=x-x(P)",
            "pullback_leading_coefficient": "c*alpha_(u,P)^m with alpha=u*y([u]P)/y(P)",
        },
        "global_balance_circuit": {
            "formula": "chi((L1*L2)/(L3*L4))",
            "admission": "ord_P(L1)+ord_P(L2)=ord_P(L3)+ord_P(L4) at every tested subgroup point",
            "regular_value": "ratio of products of exact first nonzero local coefficients",
            "important_extension": "zeros and poles may cancel across different circuit factors; no individual ratio atom is required to be regular",
            "uniform_output_negation": True,
        },
        "forbidden": [
            "per-point patches or omitted exceptional points",
            "per-curve AST fitting",
            "target-indexed orientation tables",
            "uncharged coefficient or representation advice",
        ],
        "cost_model": [
            "all [u]Q group operations are charged",
            "all line coefficient construction and evaluations are charged",
            "all local regularization, inversions, characters and sign products are charged",
            "enumerative discovery cost is not evaluator advice",
        ],
        "claim_boundary": "A negative result closes only globally divisor-balanced 2-by-2 products in this declared pulled-line dictionary.",
    }


def run() -> tuple[dict[str, object], dict[str, object]]:
    grammar = grammar_payload()
    semantics, target, total, public = build_semantics()
    screen = search(semantics, target, total)
    raw = sum(item.multiplicity for item in semantics)
    result = {
        "schema_version": "1.0",
        "experiment": "UORC-056-GLOBAL-DIVISOR-BALANCE-V4",
        "grammar_sha256": hashlib.sha256(stable_json(grammar).encode()).hexdigest(),
        "corpus": {
            "curve_count": len(public),
            "curves": public,
            "nonzero_points": total,
        },
        "template_quotient": {
            "raw_pulled_line_templates": raw,
            "unique_exact_local_semantics": len(semantics),
            "duplicates_removed": raw - len(semantics),
        },
        **screen,
        "decision": (
            "exact_global_divisor_balance_candidate_found"
            if screen["exact_search"]["candidate_found"]
            else "no_exact_globally_balanced_two_by_two_pulled_line_circuit"
        ),
        "claim_boundary": [
            "Complete only for two numerator and two denominator pulled affine lines from the declared 1,440-template dictionary.",
            "Cross-factor zero and pole cancellation is exact; no exceptional subgroup point is patched or omitted.",
            "Higher total factor count, higher-degree primitives, index-growing maps, EDS factors and unrestricted straight-line programs remain open.",
            "No external point, wallet, real key or production-sized discrete-log target is accepted.",
        ],
    }
    return grammar, result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--grammar-out",
        type=Path,
        default=Path("experiments/uorc056/global_divisor_balance_grammar.json"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("experiments/uorc056/global_divisor_balance_results.json"),
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    grammar, result = run()
    grammar_text = stable_json(grammar)
    result_text = stable_json(result)
    if args.check:
        if args.grammar_out.read_text(encoding="utf-8") != grammar_text:
            raise SystemExit("grammar artifact drifted")
        if args.out.read_text(encoding="utf-8") != result_text:
            raise SystemExit("result artifact drifted")
    else:
        args.grammar_out.write_text(grammar_text, encoding="utf-8")
        args.out.write_text(result_text, encoding="utf-8")
    print(result_text, end="")


if __name__ == "__main__":
    main()
