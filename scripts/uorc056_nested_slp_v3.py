#!/usr/bin/env python3
"""Nested field straight-line-program search for UORC-056.

Restricted to the five frozen toy curves.  No external point, scalar, curve,
key, or wallet input is accepted.  The endpoint is one quadratic character of
a nested expression.  This is distinct from multiplying characters of shallow
factors in C-SYNTH-V2.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import uorc056_transfer_synth_v2 as base

Values = tuple[tuple[int, ...], ...]

EXTRA_CONSTANTS = ("two", "neg_two")


@dataclass(frozen=True)
class Term:
    expression: str
    size: int
    values: Values
    field_add: int
    field_mul: int
    field_inv: int
    negations: int
    features: frozenset[str]
    constants: frozenset[str]
    curve_errors: tuple[int, ...]
    curve_zeros: tuple[int, ...]
    curve_bits: tuple[int, ...]

    @property
    def exact_all(self) -> bool:
        return all(error == 0 and zero == 0 for error, zero in zip(self.curve_errors, self.curve_zeros, strict=True))

    @property
    def exact_train_three(self) -> bool:
        return all(
            self.curve_errors[index] == 0 and self.curve_zeros[index] == 0
            for index in range(3)
        )


@dataclass
class SearchState:
    best_all: Term | None = None
    best_train: Term | None = None
    exact_all: list[Term] | None = None
    exact_train: list[Term] | None = None

    def __post_init__(self) -> None:
        if self.exact_all is None:
            self.exact_all = []
        if self.exact_train is None:
            self.exact_train = []


def contexts() -> tuple[base.CurveContext, ...]:
    return tuple(base.build_context(*curve) for curve in base.FROZEN_CURVES)


def compute_endpoint_metrics(
    values: Values, curve_contexts: Sequence[base.CurveContext]
) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    errors: list[int] = []
    zeros: list[int] = []
    bits_by_curve: list[int] = []
    for curve_values, context in zip(values, curve_contexts, strict=True):
        bits = 0
        zero_count = 0
        for offset, value in enumerate(curve_values):
            sign = base.quadratic_character(value, context.p)
            if sign == 0:
                zero_count += 1
            elif sign == -1:
                bits |= 1 << offset
        target = base.parity_target(context.order)
        errors.append((bits ^ target).bit_count())
        zeros.append(zero_count)
        bits_by_curve.append(bits)
    return tuple(errors), tuple(zeros), tuple(bits_by_curve)


def make_term(
    expression: str,
    size: int,
    values: Values,
    field_add: int,
    field_mul: int,
    field_inv: int,
    negations: int,
    features: Iterable[str],
    constants: Iterable[str],
    curve_contexts: Sequence[base.CurveContext],
) -> Term:
    errors, zeros, bits = compute_endpoint_metrics(values, curve_contexts)
    return Term(
        expression=expression,
        size=size,
        values=values,
        field_add=field_add,
        field_mul=field_mul,
        field_inv=field_inv,
        negations=negations,
        features=frozenset(features),
        constants=frozenset(constants),
        curve_errors=errors,
        curve_zeros=zeros,
        curve_bits=bits,
    )


def seed_terms(curve_contexts: Sequence[base.CurveContext]) -> tuple[Term, ...]:
    rows_by_curve = [
        [base.observable_row(context, k) for k in range(1, context.order)]
        for context in curve_contexts
    ]
    constants_by_curve = [base.constant_values(context) for context in curve_contexts]
    terms: list[Term] = []

    for observable in base.OBSERVABLE_NAMES:
        values: Values = tuple(
            tuple(row[observable] for row in rows) for rows in rows_by_curve
        )
        terms.append(
            make_term(
                expression=observable,
                size=0,
                values=values,
                field_add=0,
                field_mul=0,
                field_inv=0,
                negations=0,
                features=(observable,),
                constants=(),
                curve_contexts=curve_contexts,
            )
        )

    constant_names = (*base.CONSTANT_NAMES, *EXTRA_CONSTANTS)
    for constant in constant_names:
        values = tuple(
            tuple(constant_map[constant] for _ in range(context.order - 1))
            for constant_map, context in zip(
                constants_by_curve, curve_contexts, strict=True
            )
        )
        terms.append(
            make_term(
                expression=constant,
                size=0,
                values=values,
                field_add=0,
                field_mul=0,
                field_inv=0,
                negations=0,
                features=(),
                constants=(constant,),
                curve_contexts=curve_contexts,
            )
        )

    best: dict[Values, Term] = {}
    for term in terms:
        previous = best.get(term.values)
        if previous is None or term.expression < previous.expression:
            best[term.values] = term
    return tuple(sorted(best.values(), key=lambda term: term.expression))


def total_penalty(term: Term, subset: Sequence[int]) -> int:
    return sum(term.curve_errors[index] + term.curve_zeros[index] for index in subset)


def term_rank(term: Term) -> tuple[object, ...]:
    return (
        total_penalty(term, range(5)),
        total_penalty(term, range(3)),
        sum(term.curve_zeros),
        term.field_inv,
        term.field_mul,
        term.field_add + term.negations,
        term.size,
        len(term.expression),
        term.expression,
    )


def train_rank(term: Term) -> tuple[object, ...]:
    return (
        total_penalty(term, range(3)),
        total_penalty(term, range(5)),
        sum(term.curve_zeros),
        term.field_inv,
        term.field_mul,
        term.field_add + term.negations,
        term.size,
        term.expression,
    )


def observe_term(term: Term, state: SearchState, maximum_exact: int = 8) -> None:
    if state.best_all is None or term_rank(term) < term_rank(state.best_all):
        state.best_all = term
    if state.best_train is None or train_rank(term) < train_rank(state.best_train):
        state.best_train = term
    assert state.exact_all is not None and state.exact_train is not None
    if term.exact_all and len(state.exact_all) < maximum_exact:
        if all(existing.values != term.values for existing in state.exact_all):
            state.exact_all.append(term)
    if term.exact_train_three and len(state.exact_train) < maximum_exact:
        if all(existing.values != term.values for existing in state.exact_train):
            state.exact_train.append(term)


def semantic_select(terms: Sequence[Term], beam_size: int) -> tuple[Term, ...]:
    best_by_values: dict[Values, Term] = {}
    for term in terms:
        previous = best_by_values.get(term.values)
        if previous is None or term_rank(term) < term_rank(previous):
            best_by_values[term.values] = term
    ordered = sorted(best_by_values.values(), key=term_rank)
    if len(ordered) <= beam_size:
        return tuple(ordered)

    primary_count = max(1, beam_size * 3 // 4)
    selected = ordered[:primary_count]
    selected_values = {term.values for term in selected}
    signatures = {
        (term.curve_errors, term.curve_zeros) for term in selected
    }
    for term in ordered[primary_count:]:
        signature = (term.curve_errors, term.curve_zeros)
        if signature in signatures or term.values in selected_values:
            continue
        selected.append(term)
        selected_values.add(term.values)
        signatures.add(signature)
        if len(selected) >= beam_size:
            break
    if len(selected) < beam_size:
        for term in ordered[primary_count:]:
            if term.values in selected_values:
                continue
            selected.append(term)
            selected_values.add(term.values)
            if len(selected) >= beam_size:
                break
    return tuple(selected)


def bounded_append(
    buffer: list[Term], term: Term, beam_size: int
) -> list[Term]:
    buffer.append(term)
    threshold = max(beam_size * 8, 256)
    if len(buffer) >= threshold:
        return list(semantic_select(buffer, max(beam_size * 3, beam_size)))
    return buffer


def unary_term(
    operation: str,
    term: Term,
    curve_contexts: Sequence[base.CurveContext],
) -> Term | None:
    if operation == "neg":
        values: Values = tuple(
            tuple((-value) % context.p for value in curve_values)
            for curve_values, context in zip(term.values, curve_contexts, strict=True)
        )
        return make_term(
            expression=f"(-{term.expression})",
            size=term.size + 1,
            values=values,
            field_add=term.field_add,
            field_mul=term.field_mul,
            field_inv=term.field_inv,
            negations=term.negations + 1,
            features=term.features,
            constants=term.constants,
            curve_contexts=curve_contexts,
        )
    if operation == "inv":
        if any(value == 0 for curve_values in term.values for value in curve_values):
            return None
        values = tuple(
            tuple(pow(value, -1, context.p) for value in curve_values)
            for curve_values, context in zip(term.values, curve_contexts, strict=True)
        )
        return make_term(
            expression=f"inv({term.expression})",
            size=term.size + 1,
            values=values,
            field_add=term.field_add,
            field_mul=term.field_mul,
            field_inv=term.field_inv + 1,
            negations=term.negations,
            features=term.features,
            constants=term.constants,
            curve_contexts=curve_contexts,
        )
    raise ValueError(f"unknown unary operation: {operation}")


def binary_term(
    operation: str,
    left: Term,
    right: Term,
    curve_contexts: Sequence[base.CurveContext],
) -> Term:
    if operation in ("add", "mul") and right.expression < left.expression:
        left, right = right, left
    values_by_curve: list[tuple[int, ...]] = []
    for left_values, right_values, context in zip(
        left.values, right.values, curve_contexts, strict=True
    ):
        if operation == "add":
            values_by_curve.append(
                tuple((a + b) % context.p for a, b in zip(left_values, right_values, strict=True))
            )
        elif operation == "sub":
            values_by_curve.append(
                tuple((a - b) % context.p for a, b in zip(left_values, right_values, strict=True))
            )
        elif operation == "mul":
            values_by_curve.append(
                tuple((a * b) % context.p for a, b in zip(left_values, right_values, strict=True))
            )
        else:
            raise ValueError(f"unknown binary operation: {operation}")
    symbol = {"add": "+", "sub": "-", "mul": "*"}[operation]
    return make_term(
        expression=f"({left.expression}{symbol}{right.expression})",
        size=left.size + right.size + 1,
        values=tuple(values_by_curve),
        field_add=left.field_add + right.field_add + (1 if operation in ("add", "sub") else 0),
        field_mul=left.field_mul + right.field_mul + (1 if operation == "mul" else 0),
        field_inv=left.field_inv + right.field_inv,
        negations=left.negations + right.negations,
        features=left.features.union(right.features),
        constants=left.constants.union(right.constants),
        curve_contexts=curve_contexts,
    )


def generate_layer(
    size: int,
    layers: dict[int, tuple[Term, ...]],
    curve_contexts: Sequence[base.CurveContext],
    beam_size: int,
    state: SearchState,
) -> tuple[tuple[Term, ...], int]:
    buffer: list[Term] = []
    generated = 0

    for term in layers[size - 1]:
        for operation in ("neg", "inv"):
            candidate = unary_term(operation, term, curve_contexts)
            if candidate is None:
                continue
            generated += 1
            observe_term(candidate, state)
            buffer = bounded_append(buffer, candidate, beam_size)

    for left_size in range(size):
        right_size = size - 1 - left_size
        if left_size > right_size:
            continue
        left_layer = layers[left_size]
        right_layer = layers[right_size]
        for left_index, left in enumerate(left_layer):
            start = left_index if left_size == right_size else 0
            for right in right_layer[start:]:
                for operation in ("add", "mul"):
                    candidate = binary_term(operation, left, right, curve_contexts)
                    generated += 1
                    observe_term(candidate, state)
                    buffer = bounded_append(buffer, candidate, beam_size)
                candidate = binary_term("sub", left, right, curve_contexts)
                generated += 1
                observe_term(candidate, state)
                buffer = bounded_append(buffer, candidate, beam_size)
                if left.values != right.values:
                    candidate = binary_term("sub", right, left, curve_contexts)
                    generated += 1
                    observe_term(candidate, state)
                    buffer = bounded_append(buffer, candidate, beam_size)

    return semantic_select(buffer, beam_size), generated


def per_curve_validation(term: Term, curve_contexts: Sequence[base.CurveContext]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index, context in enumerate(curve_contexts):
        total = context.order - 1
        penalty = term.curve_errors[index] + term.curve_zeros[index]
        rows.append(
            {
                "curve_id": context.curve_id,
                "errors_among_nonzero_values": term.curve_errors[index],
                "endpoint_zeros": term.curve_zeros[index],
                "total": total,
                "exact": penalty == 0,
                "accuracy_with_zeros_as_failures": (total - penalty) / total,
            }
        )
    return rows


def term_cost(term: Term) -> dict[str, object]:
    operations = {
        "field_add": term.field_add,
        "field_mul": term.field_mul,
        "field_inv": term.field_inv,
        "negation": term.negations,
        "group_add_upper_bound": 0,
        "group_double_upper_bound": 0,
        "endpoint_quadratic_character": 1,
    }
    for feature in term.features:
        for name, amount in base.FEATURE_UPPER_COST[feature].items():
            if name == "group_add":
                operations["group_add_upper_bound"] += amount
            elif name == "group_double":
                operations["group_double_upper_bound"] += amount
            else:
                operations[name] += amount
    return {
        "arithmetic_gates_in_slp": term.size,
        "operation_upper_bound": operations,
        "public_features": sorted(term.features),
        "public_constants": sorted(term.constants),
        "cost_boundary": "This is an operation ledger, not an asymptotic speedup claim.",
    }


def serialize_term(term: Term | None, curve_contexts: Sequence[base.CurveContext]) -> dict[str, object] | None:
    if term is None:
        return None
    return {
        "expression": term.expression,
        "size": term.size,
        "exact_all_five": term.exact_all,
        "exact_first_three": term.exact_train_three,
        "total_penalty_all_five": total_penalty(term, range(5)),
        "total_penalty_first_three": total_penalty(term, range(3)),
        "curve_validation": per_curve_validation(term, curve_contexts),
        "cost": term_cost(term),
    }


def run(max_size: int, beam_size: int) -> dict[str, object]:
    curve_contexts = contexts()
    seeds = seed_terms(curve_contexts)
    state = SearchState()
    for seed in seeds:
        observe_term(seed, state)
    layers: dict[int, tuple[Term, ...]] = {0: seeds}
    layer_stats: list[dict[str, object]] = [
        {
            "size": 0,
            "generated": len(seeds),
            "retained": len(seeds),
            "best_all_five_penalty": min(total_penalty(term, range(5)) for term in seeds),
            "best_first_three_penalty": min(total_penalty(term, range(3)) for term in seeds),
        }
    ]

    minimum_exact_size: int | None = 0 if state.exact_all else None
    for size in range(1, max_size + 1):
        layer, generated = generate_layer(
            size, layers, curve_contexts, beam_size, state
        )
        layers[size] = layer
        layer_stats.append(
            {
                "size": size,
                "generated": generated,
                "retained": len(layer),
                "best_all_five_penalty": min(
                    (total_penalty(term, range(5)) for term in layer), default=None
                ),
                "best_first_three_penalty": min(
                    (total_penalty(term, range(3)) for term in layer), default=None
                ),
                "distinct_error_signatures": len(
                    {(term.curve_errors, term.curve_zeros) for term in layer}
                ),
            }
        )
        if state.exact_all:
            minimum_exact_size = size
            break

    assert state.exact_all is not None and state.exact_train is not None
    exact_all_sorted = sorted(state.exact_all, key=term_rank)
    exact_train_sorted = sorted(state.exact_train, key=train_rank)
    if exact_all_sorted:
        decision = "NESTED_SLP_TRANSFER_SEED_FOUND_REQUIRES_SYMBOLIC_LIFTING"
        lifting = "triggered"
    elif exact_train_sorted:
        decision = "NO_ALL_FIVE_EXACT_NESTED_SLP;_TRAIN_EXACT_SEED_ONLY"
        lifting = "not_triggered_holdout_failed"
    else:
        decision = "NO_EXACT_SEED_FOUND_IN_DECLARED_NESTED_SLP_BEAM"
        lifting = "not_triggered"

    return {
        "schema_version": "1.0",
        "experiment": "UORC-056-NESTED-SLP-V3",
        "scope": "five frozen toy curves only; no external inputs",
        "central_target": "Q=[k]G -> Y_G(x(Q))/y(Q)=(-1)^k",
        "search": {
            "max_arithmetic_gates": max_size,
            "beam_size_per_gate_count": beam_size,
            "endpoint": "one quadratic character",
            "field_specific_fitting": False,
            "free_per_curve_phase": False,
            "completeness": "all declared seeds are exhaustive; subsequent layers are deterministic beam search and do not support a general lower-bound claim",
        },
        "seed_count": len(seeds),
        "layer_statistics": layer_stats,
        "decision": decision,
        "minimum_exact_all_five_size": minimum_exact_size,
        "symbolic_lifting_status": lifting,
        "exact_all_five_candidates": [
            serialize_term(term, curve_contexts) for term in exact_all_sorted[:8]
        ],
        "exact_first_three_candidates": [
            serialize_term(term, curve_contexts) for term in exact_train_sorted[:8]
        ],
        "best_all_five_near_miss": serialize_term(state.best_all, curve_contexts),
        "best_first_three_near_miss": serialize_term(state.best_train, curve_contexts),
        "claim_boundary": [
            "A beam miss is not an arithmetic-circuit lower bound.",
            "A toy exact expression is only a transfer seed until symbolically lifted and asymptotically costed.",
            "No materialized Y_G coefficients or scalar-indexed advice are available to the grammar.",
            "No unknown production scalar is accepted or recovered.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-size", type=int, default=4)
    parser.add_argument("--beam-size", type=int, default=96)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("uorc056_nested_slp_v3_results.json"),
    )
    args = parser.parse_args()
    if args.max_size < 0 or args.max_size > 8:
        raise SystemExit("--max-size must be between 0 and 8")
    if args.beam_size < 16:
        raise SystemExit("--beam-size must be at least 16")
    payload = run(args.max_size, args.beam_size)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "experiment": payload["experiment"],
                "decision": payload["decision"],
                "seed_count": payload["seed_count"],
                "layers": payload["layer_statistics"],
                "output": str(args.out),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
