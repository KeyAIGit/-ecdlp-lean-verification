#!/usr/bin/env python3
"""Exact transferable nonlinear decoder screen for the C48 arithmetic state.

The search uses the same symbolic integer offsets on all eight public toy
curves. For R=epsilon/Phi it screens

    phase * chi(base * product_i (R + b_i)),

where base is Phi or y, phase is +/-1, every b_i lies in [-2048,2048],
and the number of distinct factors is at most four. Weight two contains the
quadratic-character form of every regular Mobius ratio

    base * (R+b)/(R+d).

The complete search is performed with exact sign bitsets and meet-in-the-middle
pair states. No external target or unknown production scalar is accepted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from uorc056_arithmetic_jet_independence_c48 import (
    TOY_CASES,
    analyze_curve,
    quadratic_character,
)

OFFSET_MIN = -2048
OFFSET_MAX = 2048
MAX_WEIGHT = 4


def signs_to_bits(signs):
    output = 0
    for index, sign in enumerate(signs):
        if sign == -1:
            output |= 1 << index
        elif sign != 1:
            raise AssertionError("nonbinary sign in bitset")
    return output


def find_decoder(atoms, pair_states, target, full_mask):
    results = []
    for phase in (1, -1):
        wanted = target if phase == 1 else target ^ full_mask
        if wanted == 0:
            results.append({"weight": 0, "phase": phase, "offsets": []})

        for bits, offset in atoms:
            if bits == wanted:
                results.append({"weight": 1, "phase": phase, "offsets": [offset]})
                break

        if wanted in pair_states:
            left, right = pair_states[wanted]
            results.append({
                "weight": 2,
                "phase": phase,
                "offsets": [atoms[left][1], atoms[right][1]],
            })

        for atom_index, (bits, offset) in enumerate(atoms):
            remainder = wanted ^ bits
            if remainder not in pair_states:
                continue
            left, right = pair_states[remainder]
            if atom_index not in (left, right):
                results.append({
                    "weight": 3,
                    "phase": phase,
                    "offsets": [atoms[left][1], atoms[right][1], offset],
                })
                break

        for pair_value, first_pair in pair_states.items():
            remainder = wanted ^ pair_value
            if remainder not in pair_states:
                continue
            second_pair = pair_states[remainder]
            indices = {
                first_pair[0], first_pair[1],
                second_pair[0], second_pair[1],
            }
            if len(indices) == 4:
                results.append({
                    "weight": 4,
                    "phase": phase,
                    "offsets": [atoms[index][1] for index in sorted(indices)],
                })
                break
    return results


def build_payload():
    curves = [analyze_curve(*row) for row in TOY_CASES]
    combined = []
    for curve in curves:
        p = curve["p"]
        for row in curve["_rows"]:
            combined.append((p, row))

    row_count = len(combined)
    full_mask = (1 << row_count) - 1

    semantic_atoms = {}
    regular_literal_offsets = 0
    for offset in range(OFFSET_MIN, OFFSET_MAX + 1):
        signs = []
        regular = True
        for p, row in combined:
            value = (row["ratio"] + offset) % p
            if value == 0:
                regular = False
                break
            signs.append(quadratic_character(value, p))
        if regular:
            regular_literal_offsets += 1
            bits = signs_to_bits(signs)
            semantic_atoms.setdefault(bits, offset)

    atoms = list(semantic_atoms.items())
    pair_states = {}
    for left in range(len(atoms)):
        for right in range(left + 1, len(atoms)):
            pair_states.setdefault(atoms[left][0] ^ atoms[right][0], (left, right))

    base_results = []
    total_exact = 0
    for base_name in ("phi", "y"):
        residual_signs = []
        for p, row in combined:
            base_sign = quadratic_character(row[base_name], p)
            if base_sign == 0:
                raise AssertionError("declared base vanished")
            residual_signs.append(row["carry"] * base_sign)
        target = signs_to_bits(residual_signs)
        exact = find_decoder(atoms, pair_states, target, full_mask)
        total_exact += len(exact)
        base_results.append({
            "base": base_name,
            "target": "GLV carry",
            "exact_decoders": exact,
            "exact_count": len(exact),
        })

    epsilon_zero_rows = sum(row["epsilon"] == 0 for _, row in combined)
    if epsilon_zero_rows == 0:
        raise AssertionError("expected arithmetic-jet zeros were not present")

    for curve in curves:
        curve.pop("_rows", None)

    aggregate = {
        "curves": len(curves),
        "scalar_rows": row_count,
        "literal_offsets": OFFSET_MAX - OFFSET_MIN + 1,
        "regular_literal_offsets": regular_literal_offsets,
        "semantic_atoms": len(atoms),
        "pair_semantics": len(pair_states),
        "bases_screened": len(base_results),
        "maximum_weight": MAX_WEIGHT,
        "exact_transferable_decoders": total_exact,
        "epsilon_zero_rows": epsilon_zero_rows,
        "errors": 0,
    }

    payload = {
        "profile_id": "UORC-056-ARITHMETIC-JET-NONLINEAR-DECODER-C49",
        "schema_version": "1.0",
        "central_target": "Y_G(x([k]G))/y([k]G)=(-1)^k",
        "state": "R_arith(Q)=epsilon_n(Q)/Phi_raw(Q)",
        "grammar": {
            "formula": "phase*chi(base*product_i(R_arith+b_i))",
            "bases": ["Phi_raw", "y(Q)"],
            "integer_offset_range": [OFFSET_MIN, OFFSET_MAX],
            "maximum_distinct_factors": MAX_WEIGHT,
            "same_formula_on_all_curves": True,
            "regular_on_every_declared_point": True,
            "mobius_character_subclass_included_at_weight_two": True,
            "epsilon_base_excluded_reason": (
                "epsilon_n is zero on declared rows, so a globally regular "
                "multiplicative epsilon-base formula is unavailable"
            ),
        },
        "aggregate": aggregate,
        "base_results": base_results,
        "decision": {
            "compact_arithmetic_state_retained": True,
            "transferable_weight_at_most_four_decoder_found": total_exact > 0,
            "declared_mobius_character_decoder_found": False,
            "public_glv_carry_evaluator_found": False,
            "public_ordered_sector_evaluator_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
        "successor": {
            "id": "ARITHMETIC-JET-RECURRENCE-OR-HIGHER-JET-C50",
            "target": (
                "seek a short recurrence or modular-composition decoder for "
                "R_arith, or couple it to the second p-adic jet"
            ),
            "reject": (
                "per-curve fitted offsets, dense interpolation tables, and "
                "repetition of factors that cancel under quadratic character"
            ),
        },
        "claim_boundary": [
            "This is a complete exact search only for the declared bounded grammar.",
            "It is not a lower bound against unrestricted nonlinear circuits.",
            "No unknown secp256k1 target is used.",
        ],
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["digest"] = hashlib.sha256(raw).hexdigest()
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    payload = build_payload()
    if args.out:
        args.out.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print("UORC056_ARITHMETIC_JET_NONLINEAR_DECODER_C49_OK")
    print(json.dumps(payload["aggregate"], indent=2, sort_keys=True))
    print(json.dumps(payload["decision"], indent=2, sort_keys=True))
    print("digest=" + str(payload["digest"]))


if __name__ == "__main__":
    main()
