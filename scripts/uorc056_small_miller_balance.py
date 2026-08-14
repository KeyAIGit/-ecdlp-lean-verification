#!/usr/bin/env python3
"""Screen divisor-balanced products of small public Miller primitives on frozen toys."""
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
    inv,
    local_line_order_and_coefficient,
    negate_sparse,
    quadratic_character,
    stable_json,
)

SMALL_MARKS = (-4, -3, -2, -1, 1, 2, 3, 4)
PULLBACKS = (1, 2, 3, 4)
PHASE_LABELS = (
    "one", "neg_one", "curve_b", "neg_curve_b", "x_G", "neg_x_G",
    "y_G", "neg_y_G", "beta_lo", "beta_hi", "x_G_plus_y_G",
    "x_G_minus_y_G",
)


@dataclass(frozen=True, order=True)
class MillerTemplate:
    a: int
    b: int
    pullback: int


@dataclass(frozen=True)
class PrimitiveSemantics:
    valuation: SparseValuation
    sign_bits: int
    representative: MillerTemplate
    multiplicity: int = 1


@dataclass(frozen=True)
class SignedAtom:
    valuation: SparseValuation
    sign_bits: int
    primitive_index: int
    exponent: int


def templates() -> Iterator[MillerTemplate]:
    for pullback in PULLBACKS:
        for i, a in enumerate(SMALL_MARKS):
            for b in SMALL_MARKS[i:]:
                if a + b:
                    yield MillerTemplate(a, b, pullback)


def miller_line(
    left: tuple[int, int], right: tuple[int, int], p: int
) -> tuple[int, int, int]:
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        raise ValueError("vertical A,-A pair is excluded")
    if left == right:
        slope = 3 * x1 * x1 * inv(2 * y1, p) % p
    else:
        slope = (y2 - y1) * inv(x2 - x1, p) % p
    return -slope % p, 1, (slope * x1 - y1) % p


def primitive_local_data(
    curve: CurveData, scalar: int, template: MillerTemplate
) -> tuple[int, int]:
    point = curve.points[scalar]
    image = curve.points[(template.pullback * scalar) % curve.n]
    left = curve.points[template.a % curve.n]
    right = curve.points[template.b % curve.n]
    total = curve.points[(template.a + template.b) % curve.n]
    assert point is not None and image is not None
    assert left is not None and right is not None and total is not None
    numerator = miller_line(left, right, curve.p)
    denominator = (1, 0, -total[0] % curve.p)
    num_order, num_leading = local_line_order_and_coefficient(
        image, *numerator, curve.p
    )
    den_order, den_leading = local_line_order_and_coefficient(
        image, *denominator, curve.p
    )
    alpha = template.pullback * image[1] * inv(point[1], curve.p) % curve.p
    scaled_num = num_leading * pow(alpha, num_order, curve.p) % curve.p
    scaled_den = den_leading * pow(alpha, den_order, curve.p) % curve.p
    return (
        num_order - den_order,
        scaled_num * inv(scaled_den, curve.p) % curve.p,
    )


def public_phases(
    curves: tuple[CurveData, ...], total: int
) -> dict[int, str]:
    phases: dict[int, str] = {
        0: "one",
        (1 << total) - 1: "uniform_output_negation",
    }
    for label in PHASE_LABELS:
        bits = 0
        admissible = True
        for curve in curves:
            sign = quadratic_character(curve.coefficients[label], curve.p)
            if sign == 0:
                admissible = False
                break
            if sign == -1:
                for k in range(1, curve.n):
                    bits |= 1 << (curve.offset + k - 1)
        if admissible:
            phases.setdefault(bits, label)
    return phases


def build_semantics() -> tuple[
    list[PrimitiveSemantics],
    int,
    int,
    dict[int, str],
    list[dict[str, object]],
]:
    curves, target, total, public = build_discovery_corpus()
    phases = public_phases(curves, total)
    quotient: dict[tuple[SparseValuation, int], tuple[MillerTemplate, int]] = {}
    for template in templates():
        valuation: list[tuple[int, int]] = []
        signs = 0
        for curve in curves:
            for k in range(1, curve.n):
                order, unit = primitive_local_data(curve, k, template)
                position = curve.offset + k - 1
                if order:
                    valuation.append((position, order))
                sign = quadratic_character(unit, curve.p)
                if sign == -1:
                    signs |= 1 << position
                elif sign != 1:
                    raise AssertionError("local Miller unit vanished")
        key = (tuple(valuation), signs)
        if key in quotient:
            representative, multiplicity = quotient[key]
            quotient[key] = representative, multiplicity + 1
        else:
            quotient[key] = template, 1
    primitives = [
        PrimitiveSemantics(valuation, signs, representative, multiplicity)
        for (valuation, signs), (representative, multiplicity) in quotient.items()
    ]
    primitives.sort(key=lambda item: (
        item.valuation, item.sign_bits, item.representative
    ))
    return primitives, target, total, phases, public


def primitive_json(
    template: MillerTemplate, exponent: int
) -> dict[str, object]:
    return {
        "exponent": exponent,
        "pullback": template.pullback,
        "miller_addition": {"a": template.a, "b": template.b},
    }


def search(
    primitives: list[PrimitiveSemantics],
    target: int,
    total: int,
    phases: dict[int, str],
) -> dict[str, object]:
    atoms: list[SignedAtom] = []
    seen: set[tuple[SparseValuation, int]] = set()
    for index, primitive in enumerate(primitives):
        for exponent in (1, -1):
            valuation = (
                primitive.valuation
                if exponent == 1
                else negate_sparse(primitive.valuation)
            )
            key = valuation, primitive.sign_bits
            if key not in seen:
                seen.add(key)
                atoms.append(
                    SignedAtom(
                        valuation,
                        primitive.sign_bits,
                        index,
                        exponent,
                    )
                )
    atoms.sort(key=lambda atom: (
        atom.valuation,
        atom.sign_bits,
        atom.primitive_index,
        atom.exponent,
    ))

    identity = SignedAtom((), 0, -1, 1)
    extended = [identity, *atoms]
    pair_states: dict[SparseValuation, dict[int, tuple[int, ...]]] = {}
    pair_count = unique_states = repeated_states = 0
    for i, left in enumerate(extended):
        for j in range(1 if i == 0 else i, len(extended)):
            right = extended[j]
            if left.primitive_index == right.primitive_index == -1:
                continue
            pair_count += 1
            divisor = add_sparse(left.valuation, right.valuation)
            sign = left.sign_bits ^ right.sign_bits
            factors = tuple(
                index for index in (i - 1, j - 1) if index >= 0
            )
            bucket = pair_states.setdefault(divisor, {})
            if sign in bucket:
                repeated_states += 1
            else:
                bucket[sign] = factors
                unique_states += 1

    exact: dict[str, object] | None = None
    best = {"matches": -1}
    for divisor, bucket in pair_states.items():
        opposite = pair_states.get(negate_sparse(divisor))
        if opposite is None:
            continue
        for sign, factors in bucket.items():
            if not divisor:
                for phase_bits, phase_label in phases.items():
                    errors = (sign ^ phase_bits ^ target).bit_count()
                    matches = max(total - errors, errors)
                    if matches > int(best["matches"]):
                        best = {
                            "matches": matches,
                            "total": total,
                            "accuracy": f"{matches / total:.9f}",
                            "public_phase": phase_label,
                            "factors": [
                                primitive_json(
                                    primitives[
                                        atoms[index].primitive_index
                                    ].representative,
                                    atoms[index].exponent,
                                )
                                for index in factors
                            ],
                        }
            if exact is not None:
                continue
            for phase_bits, phase_label in phases.items():
                other = opposite.get(target ^ phase_bits ^ sign)
                if other is not None:
                    combined = factors + other
                    exact = {
                        "candidate_found": True,
                        "public_phase": phase_label,
                        "factor_count": len(combined),
                        "factors": [
                            primitive_json(
                                primitives[
                                    atoms[index].primitive_index
                                ].representative,
                                atoms[index].exponent,
                            )
                            for index in combined
                        ],
                    }
                    break
    if exact is None:
        exact = {"candidate_found": False, "candidate": None}
    return {
        "exact_search": exact,
        "catalog": {
            "semantic_miller_primitives": len(primitives),
            "signed_semantic_atoms": len(atoms),
            "public_phase_vectors": len(phases),
            "pair_states_enumerated": pair_count,
            "unique_pair_semantic_states": unique_states,
            "repeated_pair_semantic_states": repeated_states,
            "valuation_buckets": len(pair_states),
            "maximum_states_in_one_valuation_bucket": max(
                map(len, pair_states.values())
            ),
        },
        "best_regular_weight_le_2_correlation": best,
    }


def grammar_payload() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "profile_id": "UORC-056-SMALL-MILLER-DIVISOR-BALANCE-V5",
        "primitive": {
            "formula": "g_(a,b)([u]Q)=ell_([a]G,[b]G)([u]Q)/v_([a+b]G)([u]Q)",
            "signed_marks": list(SMALL_MARKS),
            "excluded": "a+b=0, where the addition line is vertical",
            "pullbacks": list(PULLBACKS),
            "canonical_line_normalization": "ell=y-y_A-m(x-x_A); vertical denominator=x-x_(A+B)",
            "raw_count": 128,
        },
        "circuit": {
            "maximum_primitive_factors": 4,
            "exponents": [-1, 1],
            "admission": "aggregate valuation equals zero at every tested subgroup point",
            "local_value": "product of exact local unit coefficients after aggregate divisor cancellation",
            "public_phase": "one fixed symbolic public character or uniform output negation",
        },
        "cost_model": [
            "all public small multiples, pullbacks, line constructions and inversions are charged",
            "all local regularization and character operations are charged",
            "discovery enumeration is not evaluator advice",
        ],
        "forbidden": [
            "per-point patch values or omitted exceptional points",
            "per-curve selected formulas or phase fitting",
            "target-indexed orientation tables",
            "unknown-scalar-dependent coefficients",
        ],
        "claim_boundary": "A negative result closes only products/inverses of at most four declared small Miller primitives with one declared public phase.",
    }


def run() -> tuple[dict[str, object], dict[str, object]]:
    grammar = grammar_payload()
    primitives, target, total, phases, public = build_semantics()
    screen = search(primitives, target, total, phases)
    raw = sum(item.multiplicity for item in primitives)
    result = {
        "schema_version": "1.0",
        "experiment": "UORC-056-SMALL-MILLER-DIVISOR-BALANCE-V5",
        "grammar_sha256": hashlib.sha256(
            stable_json(grammar).encode()
        ).hexdigest(),
        "corpus": {
            "curve_count": len(public),
            "curves": public,
            "nonzero_points": total,
        },
        "primitive_quotient": {
            "raw_primitives": raw,
            "unique_exact_local_semantics": len(primitives),
            "duplicates_removed": raw - len(primitives),
        },
        **screen,
        "decision": (
            "exact_small_miller_candidate_found"
            if screen["exact_search"]["candidate_found"]
            else "no_exact_small_miller_divisor_balanced_circuit_weight_le_4"
        ),
        "claim_boundary": [
            "Complete only for the declared signed marks, pullbacks, public phases and at most four Miller primitives.",
            "Aggregate zero/pole cancellation is exact and all subgroup points are retained.",
            "Long addition chains, index-growing Miller functions, EDS factors, higher-degree special functions and unrestricted circuits remain open.",
            "No external point, wallet, real key or production-sized discrete-log target is accepted.",
        ],
    }
    return grammar, result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--grammar-out",
        type=Path,
        default=Path("experiments/uorc056/small_miller_balance_grammar.json"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("experiments/uorc056/small_miller_balance_results.json"),
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
