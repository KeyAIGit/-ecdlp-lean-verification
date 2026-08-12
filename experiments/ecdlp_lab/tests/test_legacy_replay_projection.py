from __future__ import annotations

import dataclasses
import unittest

from experiments.ecdlp_lab.core.canonical import sha256_json
from experiments.ecdlp_lab.core.legacy_solver_replay import (
    PublicReplayInput,
    load_legacy_replay,
)
from experiments.framework.ec_oracle import Curve


def nested_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        keys.update(value)
        for child in value.values():
            keys.update(nested_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(nested_keys(child))
    return keys


class LegacyReplayProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = load_legacy_replay()

    def test_exact_64_case_join_identity(self) -> None:
        self.assertEqual(len(self.cases), 64)
        self.assertEqual(len({case.case_id for case in self.cases}), 64)
        identities = [
            {
                "case_id": case.case_id,
                "record_index": case.validator_only.record_index,
                "curve_index": case.validator_only.curve_index,
                "generator_index": case.validator_only.generator_index,
            }
            for case in self.cases
        ]
        operations = [
            case.validator_only.legacy_group_operations for case in self.cases
        ]
        self.assertEqual(
            sha256_json(identities),
            "6e78f08ed177e708074d41abd3c58d9576de9dd72ae6a6485bb801e2fb2c52f9",
        )
        self.assertEqual(
            sha256_json(operations),
            "28e93e247296dd25a910314e7bc5fb28ae48466fde2804941d9dfa81ce49077e",
        )

    def test_projection_contains_only_public_problem_aliases(self) -> None:
        forbidden = {
            "case_id",
            "legacy_method",
            "derived_from",
            "validator_only",
            "expected_scalar",
            "candidate_scalar",
            "legacy_candidate_scalar",
            "record_index",
            "sample_ordinal",
            "curve_index",
            "generator_index",
            "legacy_group_operations",
            "legacy_memory_bytes",
        }
        for case in self.cases:
            public_input = case.to_public_input()
            self.assertIsInstance(public_input, PublicReplayInput)
            payload = public_input.as_dict()
            self.assertTrue(forbidden.isdisjoint(nested_keys(payload)))
            self.assertEqual(
                set(payload),
                {
                    "method_id",
                    "curve_catalog_sha256",
                    "curve_fixture_id",
                    "curve_id",
                    "field_bits",
                    "subgroup_order_bits",
                    "p",
                    "a",
                    "b",
                    "G",
                    "Q",
                    "ell",
                    "seed",
                },
            )

    def test_targets_are_derived_by_the_independent_oracle(self) -> None:
        for case in self.cases:
            public_input = case.to_public_input()
            curve = Curve(public_input.p, public_input.a, public_input.b)
            self.assertEqual(
                curve.scalar_mul(
                    case.validator_only.expected_scalar,
                    public_input.G,
                ),
                public_input.Q,
            )
            self.assertLess(
                case.validator_only.expected_scalar,
                public_input.ell,
            )

    def test_replay_anchor_cases_match_the_frozen_assay(self) -> None:
        first = self.cases[0]
        self.assertEqual(first.case_id, "legacy-p1-b13-bsgs-s0")
        self.assertEqual(first.validator_only.expected_scalar, 5838)
        self.assertEqual(first.validator_only.legacy_candidate_scalar, 5838)
        self.assertEqual(first.validator_only.legacy_group_operations, 164)
        self.assertEqual(first.to_public_input().p, 7639)
        self.assertEqual(first.to_public_input().Q, (7084, 6308))

        first_rho = self.cases[8]
        self.assertEqual(first_rho.case_id, "legacy-p1-b13-pollard_rho-s0")
        self.assertEqual(first_rho.to_public_input().Q, first.to_public_input().Q)
        self.assertEqual(first_rho.to_public_input().seed, 13000)
        self.assertEqual(first_rho.validator_only.legacy_group_operations, 319)

        last = self.cases[-1]
        self.assertEqual(last.case_id, "legacy-p1-b24-pollard_rho-s7")
        self.assertEqual(last.validator_only.expected_scalar, 11721220)
        self.assertEqual(last.validator_only.legacy_group_operations, 8103)
        self.assertEqual(last.to_public_input().p, 14972143)
        self.assertEqual(last.to_public_input().Q, (7519304, 3020453))
        self.assertEqual(last.to_public_input().seed, 24007)

    def test_private_evidence_is_absent_from_repr_and_public_is_frozen(
        self,
    ) -> None:
        case = self.cases[0]
        rendered = repr(case)
        self.assertNotIn(str(case.validator_only.expected_scalar), rendered)
        self.assertNotIn(str(case.validator_only.legacy_candidate_scalar), rendered)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            case.to_public_input().seed = 1  # type: ignore[misc]

    def test_derived_from_locators_are_exact(self) -> None:
        expected_functions = {
            "bsgs": "bsgs_solve",
            "pollard_rho": "pollard_rho_solve",
        }
        for case in self.cases:
            self.assertEqual(
                case.derived_from.source_path,
                "experiments/ml_structure_probe/p1_toy_scaling/run_assay.py",
            )
            self.assertEqual(
                case.derived_from.source_function,
                expected_functions[case.legacy_method],
            )
            self.assertEqual(
                case.derived_from.source_sha256,
                "6ab905adf8187729e818a92b047c83ff5f6b12d61fca95cfcd512cc3e24820c0",
            )


if __name__ == "__main__":
    unittest.main()
