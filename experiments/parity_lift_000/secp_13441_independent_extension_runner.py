#!/usr/bin/env python3
"""Entry point for package 026 with a bounded scikit-learn random state."""
from __future__ import annotations

import secp_13441_canonical_orbit_ml_cv as nonlinear
import secp_13441_independent_extension as extension

_original_model_for = nonlinear.model_for


def bounded_model_for(name: str, seed: int):
    return _original_model_for(name, int(seed) % (2**32 - 1))


nonlinear.model_for = bounded_model_for
extension.main()
