#!/usr/bin/env python3
"""Regression tests for the authoritative C36 -> C37 lineage repair."""

from __future__ import annotations

import copy
import re
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_uorc056_c36_c37_authority as authority  # noqa: E402


def _normalize(value: str) -> str:
    """Mirror the downstream resolver's branch/token normalization."""

    value = value.lower()
    value = re.sub(r"^refs/heads/", "", value)
    value = re.sub(r"^research/", "", value)
    value = re.sub(r"^uorc0*56[-_/]?", "", value)
    return re.sub(r"[^a-z0-9]+", "", value)


def _successor_matches_branch(successor: str, branch: str) -> bool:
    token = _normalize(successor)
    candidate = _normalize(branch)
    return candidate.endswith(token) or token.endswith(candidate)


class C36C37AuthorityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = authority.load_contract()

    def test_contract_is_exact_and_unambiguous(self) -> None:
        authority.validate_contract(self.contract)

    def test_regression_reproduces_the_former_successor_conflict(self) -> None:
        self.assertFalse(
            _successor_matches_branch(
                authority.PLANNED_SUCCESSOR,
                authority.REALIZED_CHILD_BRANCH,
            )
        )
        self.assertTrue(
            _successor_matches_branch(
                self.contract["successor"],
                authority.REALIZED_CHILD_BRANCH,
            )
        )

    def test_actual_c37_realizes_the_preserved_planned_identifier(self) -> None:
        relations = {
            (row["type"], row["source"], row["target"])
            for row in self.contract["authority"]["relations"]
        }
        self.assertIn(
            ("REALIZES", "realized_child", "planned_successor"),
            relations,
        )
        self.assertEqual(
            self.contract["planned_successor"],
            authority.PLANNED_SUCCESSOR,
        )

    def test_parallel_c36_is_never_the_c37_parent(self) -> None:
        relations = {
            (row["type"], row["source"], row["target"])
            for row in self.contract["authority"]["relations"]
        }
        self.assertEqual(
            {
                row
                for row in relations
                if row[0] == "PARENT" and row[1] == "realized_child"
            },
            {("PARENT", "realized_child", "canonical_parent")},
        )
        self.assertNotIn(
            ("PARENT", "realized_child", "parallel_c36"),
            relations,
        )
        self.assertNotIn(
            ("SUCCESSOR", "parallel_c36", "realized_child"),
            relations,
        )

    def test_parent_swap_to_parallel_c36_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.contract)
        for row in mutated["authority"]["relations"]:
            if row["type"] == "PARENT":
                row["target"] = "parallel_c36"
        with self.assertRaisesRegex(authority.AuthorityError, "typed authority relations"):
            authority.validate_contract(mutated)

    def test_parallel_package_cannot_be_made_authorizing(self) -> None:
        mutated = copy.deepcopy(self.contract)
        mutated["authority"]["entities"]["parallel_c36"]["authorizing"] = True
        with self.assertRaisesRegex(authority.AuthorityError, "authorizing flag"):
            authority.validate_contract(mutated)

    def test_no_scientific_package_is_silently_superseded(self) -> None:
        self.assertEqual(
            self.contract["authority"]["supersession_relations"],
            [],
        )
        self.assertFalse(
            any(
                row["type"] == "SUPERSEDES"
                for row in self.contract["authority"]["relations"]
            )
        )


if __name__ == "__main__":
    unittest.main()
