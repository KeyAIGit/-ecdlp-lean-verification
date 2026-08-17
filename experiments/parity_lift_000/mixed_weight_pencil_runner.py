#!/usr/bin/env python3
"""Serialization-safe launcher for mixed_weight_pencil_screen.py."""
from __future__ import annotations

import json
import runpy
from pathlib import Path
from typing import Any

import numpy as np

_ORIGINAL_DUMPS = json.dumps


def _numpy_default(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(
        f"Object of type {value.__class__.__name__} is not JSON serializable"
    )


def _safe_dumps(value: Any, *args: Any, **kwargs: Any) -> str:
    kwargs.setdefault("default", _numpy_default)
    return _ORIGINAL_DUMPS(value, *args, **kwargs)


json.dumps = _safe_dumps  # type: ignore[assignment]
runpy.run_path(
    str(Path(__file__).with_name("mixed_weight_pencil_screen.py")),
    run_name="__main__",
)
