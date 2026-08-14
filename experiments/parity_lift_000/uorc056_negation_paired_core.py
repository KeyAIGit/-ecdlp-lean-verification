#!/usr/bin/env python3
"""Shared exact arithmetic helpers for UORC056 C20."""
from __future__ import annotations

import importlib.util
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
C19_PATHS = [
    HERE / "uorc056_odd_rational_functional_boundary.py",
    pathlib.Path("experiments/parity_lift_000/uorc056_odd_rational_functional_boundary.py"),
    pathlib.Path("/mnt/data/c19_work/uorc056_odd_rational_functional_boundary.py"),
]
for _path in C19_PATHS:
    if _path.exists():
        _spec = importlib.util.spec_from_file_location("uorc056_c19_for_c20", _path)
        c19 = importlib.util.module_from_spec(_spec)
        sys.modules["uorc056_c19_for_c20"] = c19
        assert _spec.loader is not None
        _spec.loader.exec_module(c19)
        break
else:
    raise FileNotFoundError("C19 module not found")

c17 = c19.c17
SECP_N = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16)
DICKSON_ODD_INDICES = (1, 3, 5, 7, 9, 15, 31)
LOCAL_SERIES_TERMS = 16
PROFILE_SERIES_TERMS = 24
CORPUS_SPLIT = {43: "discovery", 61: "discovery", 67: "discovery",
                79: "validation", 97: "validation",
                127: "held_out", 163: "held_out"}

def rf_neg(C, r):
    return c19.rf_negation_pullback(C, r)

def rf_eq(C, left, right) -> bool:
    return C.rf_norm(left) == C.rf_norm(right)

def trace3(C, r):
    r1 = C.rf_phi(r)
    r2 = C.rf_phi(r1)
    return C.rf_add(C.rf_add(r, r1), r2)

def norm3(C, r):
    r1 = C.rf_phi(r)
    r2 = C.rf_phi(r1)
    return C.rf_mul(C.rf_mul(r, r1), r2)

def support_profile(C, r, points, terms: int = PROFILE_SERIES_TERMS) -> dict[str, object]:
    values = [C.series_val(r, point, K=terms) for point in points[1:]]
    return {
        "affine_nonzero_support": sum(value != 0 for value in values),
        "affine_nonzero_pole_degree": sum(max(-value, 0) for value in values),
        "valuation_histogram": {
            str(value): values.count(value) for value in sorted(set(values))
        },
    }

def pair_exception_indices(endpoint: list[int]) -> list[int]:
    n = len(endpoint)
    return [
        k for k in range(n)
        if not (endpoint[k] in (-1, 1) and endpoint[-k % n] == -endpoint[k])
    ]
