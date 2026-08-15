#!/usr/bin/env python3
"""CLI and public imports for UORC-056 shared parity Cauchy barrier V19."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from uorc056_shared_parity_cauchy_core import verify_exhaustive_cauchy_minors
from uorc056_shared_parity_fourier import (
    bilinear_leaf_sum_bound,
    pair_sum_cover_bound,
)
from uorc056_shared_parity_records import (
    EXHAUSTIVE_CAUCHY_ORDERS,
    FROZEN_INSTANCES,
    SECP256K1_N,
    cycle_record,
    secp256k1_record,
)
from uorc056_shared_parity_report import PROFILE_ID, run

DEFAULT_OUTPUT = Path("experiments/uorc056/shared_parity_cauchy_barrier_results.json")


def stable_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = stable_json(run())
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("V19 shared parity Cauchy artifact drift")
        print("UORC056_SHARED_PARITY_CAUCHY_BARRIER_V19_OK")
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
