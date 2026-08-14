#!/usr/bin/env python3
"""Residual correction for the deterministic V2 all-curve near miss.

The executable is toy-only and accepts no external inputs.  It exhaustively
checks whether the selected V2 near miss can be corrected by one or two further
uniform sign atoms.  It also records transport and spectral diagnostics of the
remaining error vector.
"""
from __future__ import annotations

import argparse
import cmath
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import uorc056_transfer_synth_v2 as base


@dataclass(frozen=True)
class CorrectionSearch:
    exact: tuple[tuple[int, ...], ...]
    best: tuple[int, ...]
    best_errors: int
    searched_singles: int
    searched_pairs: int


def symmetric_difference_indices(*groups: Sequence[int]) -> tuple[int, ...]:
    active: set[int] = set()
    for group in groups:
        for index in group:
            if index in active:
                active.remove(index)
            else:
                active.add(index)
    return tuple(sorted(active))


def search_corrections(
    pool: Sequence[base.PoolEntry],
    residual: int,
    maximum_exact: int = 8,
) -> CorrectionSearch:
    exact: list[tuple[int, ...]] = []
    best: tuple[int, ...] = ()
    best_errors = residual.bit_count()

    for entry in pool:
        errors = (entry.vector ^ residual).bit_count()
        candidate = (entry.atom_index,)
        if errors == 0 and candidate not in exact and len(exact) < maximum_exact:
            exact.append(candidate)
        if (errors, candidate) < (best_errors, best):
            best_errors = errors
            best = candidate

    searched_pairs = 0
    for left in range(len(pool)):
        left_entry = pool[left]
        for right in range(left + 1, len(pool)):
            right_entry = pool[right]
            searched_pairs += 1
            candidate = tuple(sorted((left_entry.atom_index, right_entry.atom_index)))
            errors = (left_entry.vector ^ right_entry.vector ^ residual).bit_count()
            if errors == 0 and candidate not in exact and len(exact) < maximum_exact:
                exact.append(candidate)
            if (errors, candidate) < (best_errors, best):
                best_errors = errors
                best = candidate

    return CorrectionSearch(
        exact=tuple(sorted(exact)),
        best=best,
        best_errors=best_errors,
        searched_singles=len(pool),
        searched_pairs=searched_pairs,
    )


def candidate_curve_bits(
    compiled: Sequence[base.CompiledAtom],
    candidate: Sequence[int],
    curve_index: int,
) -> int:
    bits = 0
    for atom_index in candidate:
        atom_bits = compiled[atom_index].curve_bits[curve_index]
        if atom_bits is None:
            raise AssertionError("selected all-curve candidate became undefined")
        bits ^= atom_bits
    return bits


def bit_at(bits: int, k: int) -> int:
    return (bits >> (k - 1)) & 1


def action_disagreement(bits: int, multiplier: int, order: int) -> int:
    multiplier %= order
    if multiplier == 0:
        raise ValueError("action multiplier must be nonzero")
    return sum(
        bit_at(bits, k) != bit_at(bits, multiplier * k % order)
        for k in range(1, order)
    )


def glv_lambda(context: base.CurveContext) -> int:
    gx, gy = context.generator
    phi_g = (context.beta * gx % context.p, gy)
    try:
        index = context.points.index(phi_g)
    except ValueError as exc:
        raise AssertionError("canonical cubic-CM image is outside the frozen orbit") from exc
    if index == 0:
        raise AssertionError("nontrivial CM image cannot be the identity")
    return index


def residue_class_predictor(bits: int, order: int) -> dict[str, object]:
    total = order - 1
    ones = bits.bit_count()
    baseline = max(ones, total - ones) / total
    best: dict[str, object] | None = None
    for modulus in range(2, 17):
        predictions: dict[int, int] = {}
        matches = 0
        for residue in range(modulus):
            labels = [
                bit_at(bits, k)
                for k in range(1, order)
                if k % modulus == residue
            ]
            if not labels:
                continue
            majority = 1 if sum(labels) * 2 > len(labels) else 0
            predictions[residue] = majority
            matches += sum(label == majority for label in labels)
        accuracy = matches / total
        row = {
            "modulus": modulus,
            "accuracy": accuracy,
            "global_majority_baseline": baseline,
            "lift": accuracy - baseline,
            "class_predictions": {str(key): value for key, value in predictions.items()},
        }
        if best is None or (row["lift"], row["accuracy"], -modulus) > (
            best["lift"],
            best["accuracy"],
            -best["modulus"],
        ):
            best = row
    assert best is not None
    return best


def top_fourier(bits: int, order: int, count: int = 5) -> list[dict[str, float | int]]:
    sequence = [0.0] + [float(bit_at(bits, k)) for k in range(1, order)]
    mean = sum(sequence) / order
    rows: list[tuple[float, int, complex]] = []
    for frequency in range(1, order):
        coefficient = sum(
            (value - mean)
            * cmath.exp(-2j * math.pi * frequency * index / order)
            for index, value in enumerate(sequence)
        ) / order
        rows.append((abs(coefficient), frequency, coefficient))
    rows.sort(key=lambda row: (-row[0], row[1]))
    return [
        {
            "frequency": frequency,
            "magnitude": magnitude,
            "real": coefficient.real,
            "imag": coefficient.imag,
        }
        for magnitude, frequency, coefficient in rows[:count]
    ]


def curve_residual_diagnostic(
    context: base.CurveContext,
    residual_bits: int,
) -> dict[str, object]:
    order = context.order
    lambda_value = glv_lambda(context)
    error_positions = [k for k in range(1, order) if bit_at(residual_bits, k)]
    return {
        "curve_id": context.curve_id,
        "errors": len(error_positions),
        "total": order - 1,
        "error_positions": error_positions,
        "transport_disagreement": {
            "negation_k_to_minus_k": action_disagreement(residual_bits, -1, order),
            "doubling_k_to_2k": action_disagreement(residual_bits, 2, order),
            "canonical_glv_k_to_lambda_k": action_disagreement(
                residual_bits, lambda_value, order
            ),
            "lambda": lambda_value,
        },
        "best_modular_predictor": residue_class_predictor(residual_bits, order),
        "top_nonconstant_fourier": top_fourier(residual_bits, order),
    }


def serialize_circuit(
    compiled: Sequence[base.CompiledAtom],
    contexts: Sequence[base.CurveContext],
    indices: Sequence[int],
) -> dict[str, object]:
    return base.serialize_candidate(compiled, contexts, indices)


def run(beam_size: int) -> dict[str, object]:
    contexts = tuple(base.build_context(*curve) for curve in base.FROZEN_CURVES)
    specs = base.generate_specs()
    compiled = base.compile_atoms(contexts, specs)
    subset = tuple(range(len(contexts)))
    pool = base.build_pool(compiled, contexts, subset)
    target = base.packed_target(contexts, subset)

    near = base.near_miss_beam(
        compiled,
        contexts,
        subset,
        beam_size=beam_size,
    )
    atom_id_to_index = {
        atom.spec.atom_id: index for index, atom in enumerate(compiled)
    }
    selected = tuple(atom_id_to_index[atom_id] for atom_id in near["atom_ids"])
    selected_vector = 0
    for atom_index in selected:
        packed = base.pack_bits(compiled[atom_index].curve_bits, contexts, subset)
        if packed is None:
            raise AssertionError("V2 near miss is not defined on all curves")
        selected_vector ^= packed
    residual = target ^ selected_vector

    correction = search_corrections(pool, residual)
    exact_corrected: list[dict[str, object]] = []
    for correction_indices in correction.exact:
        combined = symmetric_difference_indices(selected, correction_indices)
        exact_corrected.append(
            {
                "correction_atom_ids": [
                    compiled[index].spec.atom_id for index in correction_indices
                ],
                "actual_combined_weight": len(combined),
                "circuit": serialize_circuit(compiled, contexts, combined),
            }
        )

    best_combined = symmetric_difference_indices(selected, correction.best)
    best_validation = base.evaluate_candidate(compiled, contexts, best_combined)
    best_errors = sum(
        row["errors"] for row in best_validation if row["errors"] is not None
    )

    residual_by_curve: list[dict[str, object]] = []
    for curve_index, context in enumerate(contexts):
        curve_residual = (
            base.parity_target(context.order)
            ^ candidate_curve_bits(compiled, selected, curve_index)
        )
        residual_by_curve.append(curve_residual_diagnostic(context, curve_residual))

    if exact_corrected:
        decision = "EXACT_ONE_OR_TWO_ATOM_RESIDUAL_CORRECTION_FOUND"
        lifting = "triggered_for_corrected_transfer_seed"
    else:
        decision = "NO_EXACT_ONE_OR_TWO_ATOM_CORRECTION_TO_SELECTED_V2_NEAR_MISS"
        lifting = "not_triggered"

    return {
        "schema_version": "1.0",
        "experiment": "UORC-056-RESIDUAL-CORRECTION-V4",
        "scope": "five frozen toy curves only; no external inputs",
        "central_target": "Q=[k]G -> Y_G(x(Q))/y(Q)=(-1)^k",
        "selected_v2_near_miss": {
            "formula": near["formula"],
            "weight": near["weight"],
            "errors": residual.bit_count(),
            "total": base.packed_length(contexts, subset),
            "accuracy": near["subset_accuracy"],
            "atom_ids": near["atom_ids"],
        },
        "correction_search": {
            "all_curve_semantic_atom_pool": len(pool),
            "searched_singles": correction.searched_singles,
            "searched_pairs": correction.searched_pairs,
            "exact_corrections": exact_corrected,
            "best_nonexact_correction_atom_ids": [
                compiled[index].spec.atom_id for index in correction.best
            ],
            "best_correction_residual_errors": correction.best_errors,
            "best_combined_actual_weight": len(best_combined),
            "best_combined_formula": serialize_circuit(
                compiled, contexts, best_combined
            )["formula"],
            "best_combined_total_errors": best_errors,
            "best_combined_validation": best_validation,
        },
        "residual_diagnostics": residual_by_curve,
        "decision": decision,
        "symbolic_lifting_status": lifting,
        "task_status": [
            {"task": 26, "name": "select_deterministic_v2_residual", "status": "complete"},
            {"task": 27, "name": "exhaust_one_and_two_atom_corrections", "status": "complete"},
            {"task": 28, "name": "measure_negation_doubling_glv_transport", "status": "complete"},
            {"task": 29, "name": "measure_modular_and_fourier_residual_structure", "status": "complete"},
            {"task": 30, "name": "activate_symbolic_lift_or_next_grammar", "status": lifting},
        ],
        "claim_boundary": [
            "The correction search is exhaustive only relative to the selected V2 near miss and one or two additional admitted atoms.",
            "Failure is not a complete weight-six lower bound.",
            "Modular and Fourier fits are diagnostics using known toy indices, not evaluators from Q.",
            "No unknown production scalar is accepted or recovered.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--beam-size", type=int, default=192)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("uorc056_residual_correction_v4_results.json"),
    )
    args = parser.parse_args()
    if args.beam_size < 8:
        raise SystemExit("--beam-size must be at least 8")
    payload = run(args.beam_size)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "experiment": payload["experiment"],
                "decision": payload["decision"],
                "selected_errors": payload["selected_v2_near_miss"]["errors"],
                "best_corrected_errors": payload["correction_search"]["best_combined_total_errors"],
                "exact_corrections": len(payload["correction_search"]["exact_corrections"]),
                "output": str(args.out),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
