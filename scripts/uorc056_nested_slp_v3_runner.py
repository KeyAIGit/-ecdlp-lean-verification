#!/usr/bin/env python3
"""Validated entry point for UORC-056-NESTED-SLP-V3.

The core module was intentionally kept immutable after first publication.  This
entry point installs the corrected endpoint metric: a zero is an undefined
endpoint and is charged once; it is not also counted as a sign mismatch.
"""
from __future__ import annotations

from typing import Sequence

import uorc056_nested_slp_v3 as implementation
import uorc056_transfer_synth_v2 as base


def corrected_endpoint_metrics(
    values: implementation.Values,
    curve_contexts: Sequence[base.CurveContext],
) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    errors: list[int] = []
    zeros: list[int] = []
    bits_by_curve: list[int] = []
    for curve_values, context in zip(values, curve_contexts, strict=True):
        bits = 0
        error_count = 0
        zero_count = 0
        for offset, value in enumerate(curve_values):
            k = offset + 1
            target_sign = -1 if k & 1 else 1
            sign = base.quadratic_character(value, context.p)
            if sign == 0:
                zero_count += 1
                continue
            if sign == -1:
                bits |= 1 << offset
            if sign != target_sign:
                error_count += 1
        errors.append(error_count)
        zeros.append(zero_count)
        bits_by_curve.append(bits)
    return tuple(errors), tuple(zeros), tuple(bits_by_curve)


implementation.compute_endpoint_metrics = corrected_endpoint_metrics


if __name__ == "__main__":
    implementation.main()
