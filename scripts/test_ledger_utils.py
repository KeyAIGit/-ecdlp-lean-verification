#!/usr/bin/env python3
"""Regression tests for VERIFIED.md grouped-reference parsing."""
from __future__ import annotations

from pathlib import Path

from ledger_utils import extract_files, parse_ledger

ROOT = Path(__file__).resolve().parent.parent
GROUPED_FILES = [
    "Ecdlp/Proved/ShamirSSS.lean",
    "Ecdlp/Proved/GlvTorsionAction.lean",
    "Ecdlp/Proved/ScalarGroupStructure.lean",
]


def test_braced_file_group() -> None:
    cell = "Ecdlp/Proved/{ShamirSSS,GlvTorsionAction,ScalarGroupStructure}.lean"
    assert extract_files(ROOT, cell) == GROUPED_FILES


def test_wildcard_row_keeps_file_scope() -> None:
    rows = parse_ledger(ROOT)
    matches = [row for row in rows if row["theorem_cell"] == "`Ecdlp.*`"]
    assert len(matches) == 1
    assert matches[0]["files"] == GROUPED_FILES


def main() -> int:
    tests = [test_braced_file_group, test_wildcard_row_keeps_file_scope]
    for test in tests:
        test()
        print(f"ok  {test.__name__}")
    print(f"\nall {len(tests)} ledger-parser fixtures passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
