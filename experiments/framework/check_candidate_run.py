#!/usr/bin/env python3
"""Validate one candidate record against the current decision substrate."""
from __future__ import annotations

import sys
from pathlib import Path

from candidate_contract import load_decisions, load_record, validate_record

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python experiments/framework/check_candidate_run.py RECORD.json")
        return 2
    path = Path(sys.argv[1])
    if not path.is_absolute():
        path = ROOT / path
    try:
        record = load_record(path)
        errors = validate_record(record, load_decisions(ROOT))
    except (OSError, ValueError) as error:
        print(f"candidate record FAILED: {error}")
        return 1
    if errors:
        print(f"candidate record FAILED: {path}")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"candidate record OK: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
