#!/usr/bin/env python3
"""Regressions for the C43/C43B composed-frontier authority decision."""

from __future__ import annotations

import copy
import unittest

from check_uorc056_c43_composed_authority import (
    AuthorityError,
    C43,
    C43B,
    C43B_ENTITY,
    C43_ENTITY,
    COMPOSED_ENTITY,
    COMPOSITION,
    EXCLUDED_ENTITY,
    GENERAL_CLAIMS,
    LOCAL_CLAIMS,
    OPEN_ENTITY,
    load_record,
    resolve_composed_frontier,
    validate_git,
    validate_record,
)


class C43ComposedAuthorityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record = load_record()

    def entity(self, record: dict, entity_id: str) -> dict:
        return next(
            row
            for row in record["authority"]["entities"]
            if row["entity_id"] == entity_id
        )

    def test_exact_static_and_git_authority(self) -> None:
        validate_git(self.record)
        projection = resolve_composed_frontier(self.record)
        self.assertEqual(projection["carrier_entity_id"], C43B_ENTITY)
        self.assertEqual(projection["carrier_scientific_head_sha"], C43B)
        self.assertEqual(projection["composition_commit_sha"], COMPOSITION)
        self.assertEqual(
            projection["inherited_entity_ids"],
            tuple(sorted((C43_ENTITY, C43B_ENTITY))),
        )

    def test_equal_siblings_without_composition_fail_closed(self) -> None:
        broken = copy.deepcopy(self.record)
        broken["authority"]["entities"] = [
            row
            for row in broken["authority"]["entities"]
            if row["entity_id"] != COMPOSED_ENTITY
        ]
        broken["authority"]["relations"] = [
            row
            for row in broken["authority"]["relations"]
            if row["subject"] != COMPOSED_ENTITY
        ]
        with self.assertRaisesRegex(AuthorityError, "composed state"):
            resolve_composed_frontier(broken)

    def test_resolution_ignores_recency_pr_number_and_input_order(self) -> None:
        expected = resolve_composed_frontier(self.record)
        mutated = copy.deepcopy(self.record)
        mutated["authority"]["entities"].reverse()
        mutated["authority"]["relations"].reverse()
        mutated["authority"]["source_bindings"].reverse()
        for index, row in enumerate(mutated["authority"]["entities"]):
            if "advisory_pr_number" in row:
                row["advisory_pr_number"] = 9000 - index
            row["observed_at_non_authorizing"] = f"2099-01-{index + 1:02d}T00:00:00Z"
        self.assertEqual(resolve_composed_frontier(mutated), expected)

    def test_both_exact_provenances_and_all_claims_are_required(self) -> None:
        general = self.entity(self.record, C43_ENTITY)
        local = self.entity(self.record, C43B_ENTITY)
        self.assertEqual(general["commit_sha"], C43)
        self.assertEqual(local["commit_sha"], C43B)
        self.assertEqual(set(general["claim_locators"]), GENERAL_CLAIMS)
        self.assertEqual(set(local["claim_locators"]), LOCAL_CLAIMS)
        for entity_id in (C43_ENTITY, C43B_ENTITY):
            broken = copy.deepcopy(self.record)
            self.entity(broken, entity_id)["claim_locators"].pop()
            with self.assertRaisesRegex(AuthorityError, "claims are incomplete"):
                validate_record(broken)

    def test_superseded_or_unrelated_package_cannot_be_carrier(self) -> None:
        superseded = copy.deepcopy(self.record)
        self.entity(superseded, C43B_ENTITY)["authority_status"] = "SUPERSEDED"
        with self.assertRaisesRegex(AuthorityError, "cannot carry"):
            resolve_composed_frontier(superseded)

        unrelated = copy.deepcopy(self.record)
        relation = next(
            row
            for row in unrelated["authority"]["relations"]
            if row["relation"] == "FRONTIER_CARRIER"
        )
        relation["object"] = EXCLUDED_ENTITY
        with self.assertRaisesRegex(AuthorityError, "composition member"):
            resolve_composed_frontier(unrelated)

    def test_no_false_parent_or_supersession_relation_is_accepted(self) -> None:
        for relation in (
            {
                "relation": "SUPERSEDES",
                "subject": C43B_ENTITY,
                "object": C43_ENTITY,
            },
            {
                "relation": "DECLARED_PARENT",
                "subject": C43B_ENTITY,
                "object": C43_ENTITY,
            },
        ):
            broken = copy.deepcopy(self.record)
            broken["authority"]["relations"].append(relation)
            with self.assertRaises(AuthorityError):
                validate_record(broken)

    def test_c44_stays_an_exact_unimplemented_open_problem(self) -> None:
        open_problem = self.entity(self.record, OPEN_ENTITY)
        self.assertEqual(open_problem["planned_id"], "ORDERED-SECTOR-TRANSPORT-C44")
        self.assertEqual(open_problem["target"], "public unsquared evaluator for J_G(x(Q))")
        self.assertFalse(open_problem["implementation_authorized"])
        self.assertIsNone(open_problem["implementation_branch"])
        self.assertIsNone(open_problem["implementation_commit_sha"])
        for field, value in (
            ("implementation_authorized", True),
            ("implementation_branch", "research/unauthorized-c44"),
            ("implementation_commit_sha", "0" * 40),
        ):
            broken = copy.deepcopy(self.record)
            self.entity(broken, OPEN_ENTITY)[field] = value
            with self.assertRaisesRegex(AuthorityError, "C44"):
                validate_record(broken)


if __name__ == "__main__":
    unittest.main()
