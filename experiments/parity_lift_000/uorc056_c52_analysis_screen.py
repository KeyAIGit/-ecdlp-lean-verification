#!/usr/bin/env python3
"""Uniform character-span screens for C52."""
from __future__ import annotations

from typing import Any

from uorc056_c52_deformation_core import quadratic_character
from uorc056_c52_analysis_primitives import (
    COEFFICIENT_NAMES, FEATURE_NAMES, PAIR_FEATURES,
    XorBasis, bit_vector,
)


def uniform_structural_character_screen(auxiliaries: list[dict[str, Any]]) -> dict[str, Any]:
    target_signs: list[int] = []
    for auxiliary in auxiliaries:
        target_signs.extend(-1 if parity else 1 for parity in auxiliary["parities"])
    target = bit_vector(target_signs)
    basis = XorBasis()
    declared = valid = 0
    exact_single = []

    for feature in FEATURE_NAMES:
        for shift_name in COEFFICIENT_NAMES:
            declared += 1
            signs: list[int] = []
            good = True
            for auxiliary in auxiliaries:
                p = auxiliary["context"]["p"]
                shift = auxiliary["coefficients"][shift_name]
                for value in auxiliary["feature_columns"][feature]:
                    sign = quadratic_character(value + shift, p)
                    if sign == 0:
                        good = False
                        break
                    signs.append(sign)
                if not good:
                    break
            if not good:
                continue
            valid += 1
            vector = bit_vector(signs)
            basis.add(vector)
            if vector == target:
                exact_single.append({"feature": feature, "shift": shift_name})

    for left, right in PAIR_FEATURES:
        for alpha_name in COEFFICIENT_NAMES:
            for shift_name in COEFFICIENT_NAMES:
                declared += 1
                signs = []
                good = True
                for auxiliary in auxiliaries:
                    p = auxiliary["context"]["p"]
                    alpha = auxiliary["coefficients"][alpha_name]
                    shift = auxiliary["coefficients"][shift_name]
                    for lvalue, rvalue in zip(
                        auxiliary["feature_columns"][left],
                        auxiliary["feature_columns"][right],
                    ):
                        sign = quadratic_character(lvalue + alpha * rvalue + shift, p)
                        if sign == 0:
                            good = False
                            break
                        signs.append(sign)
                    if not good:
                        break
                if not good:
                    continue
                valid += 1
                vector = bit_vector(signs)
                basis.add(vector)
                if vector == target:
                    exact_single.append({
                        "left": left, "right": right,
                        "alpha": alpha_name, "shift": shift_name,
                    })

    return {
        "curves": len(auxiliaries),
        "rows": len(target_signs),
        "declared_atoms": declared,
        "valid_atoms": valid,
        "span_rank": basis.rank,
        "target_in_arbitrary_product_span": basis.contains(target),
        "exact_single_atoms": exact_single,
    }


def full_small_curve_pair_affine_screen(auxiliary: dict[str, Any]) -> dict[str, Any]:
    p = auxiliary["context"]["p"]
    if p != 43:
        raise AssertionError("complete screen is pinned to p=43")
    target_signs = [-1 if parity else 1 for parity in auxiliary["parities"]]
    target = bit_vector(target_signs)
    basis = XorBasis()
    declared = valid = 0
    survivors = []
    triples = (
        [(1, b, c) for b in range(p) for c in range(p)]
        + [(0, 1, c) for c in range(p)]
        + [(0, 0, 1)]
    )
    for left, right in PAIR_FEATURES:
        xs = auxiliary["feature_columns"][left]
        ys = auxiliary["feature_columns"][right]
        for a, b, c in triples:
            declared += 1
            signs = [quadratic_character(a * x + b * y + c, p) for x, y in zip(xs, ys)]
            if 0 in signs:
                continue
            valid += 1
            vector = bit_vector(signs)
            basis.add(vector)
            if vector == target:
                survivors.append({
                    "left": left,
                    "right": right,
                    "coefficients": [a, b, c],
                })
    return {
        "p": p,
        "rows": len(target_signs),
        "pairs": len(PAIR_FEATURES),
        "declared_projective_atoms": declared,
        "valid_atoms": valid,
        "span_rank": basis.rank,
        "target_in_arbitrary_product_span": basis.contains(target),
        "exact_single_survivors": survivors,
    }
