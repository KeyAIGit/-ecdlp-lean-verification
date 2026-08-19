#!/usr/bin/env python3
"""Assemble the exact C52 curve replay and decoder screens."""
from __future__ import annotations

from typing import Any

from uorc056_c52_deformation_core import FROZEN, HELD_OUT
from uorc056_c52_analysis_curve import analyze_curve
from uorc056_c52_analysis_screen import (
    full_small_curve_pair_affine_screen,
    uniform_structural_character_screen,
)


def build_analysis_payload() -> dict[str, Any]:
    results = []
    auxiliaries = []
    for index, row in enumerate(FROZEN):
        result, auxiliary = analyze_curve(row, f"frozen-{index + 1}")
        results.append(result)
        auxiliaries.append(auxiliary)
    for index, row in enumerate(HELD_OUT):
        result, auxiliary = analyze_curve(row, f"heldout-{index + 1}")
        results.append(result)
        auxiliaries.append(auxiliary)
    return {
        "curves": results,
        "uniform_structural_character_screen": uniform_structural_character_screen(auxiliaries),
        "complete_small_curve_pair_affine_screen": full_small_curve_pair_affine_screen(auxiliaries[0]),
    }
