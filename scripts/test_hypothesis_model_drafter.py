#!/usr/bin/env python3
"""Regression tests for the non-executing model-assisted draft layer."""

from __future__ import annotations

import copy
import json
import unittest

from hypothesis_model_drafter import (
    POLICY_PATH,
    build_request_packets,
    classify_http_error,
    load_json,
    parse_fragment,
    validate_policy,
)


class HypothesisModelDrafterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load_json(POLICY_PATH)
        validate_policy(cls.policy)
        cls.state = load_json(POLICY_PATH.parents[1] / cls.policy["source_state"])

    def test_dry_request_plan_is_deterministic_and_non_executable(self) -> None:
        left = build_request_packets(self.policy, self.state, limit=10)
        right = build_request_packets(self.policy, self.state, limit=10)
        self.assertEqual(left, right)
        self.assertEqual(10, len(left))
        self.assertTrue(all(item["authorization"] == "none" for item in left))
        self.assertTrue(all(item["executable"] is False for item in left))
        self.assertEqual(10, len({item["request_sha256"] for item in left}))

    def test_drafter_policy_cannot_cross_authorization_boundary(self) -> None:
        changed = copy.deepcopy(self.policy)
        changed["safety"]["authorized_count"] = 1
        with self.assertRaises(ValueError):
            validate_policy(changed)
        changed = copy.deepcopy(self.policy)
        changed["safety"]["recommended_count"] = 1
        with self.assertRaises(ValueError):
            validate_policy(changed)
        changed = copy.deepcopy(self.policy)
        changed["limits"]["max_concurrency"] = 2
        with self.assertRaises(ValueError):
            validate_policy(changed)

    def test_fragment_requires_exact_fields_and_boolean_abstention(self) -> None:
        fields = self.policy["output_contract"]["required_fields"]
        value = {
            field: ([] if field == "missing_evidence" else "fixture")
            for field in fields
        }
        value["abstain"] = True
        fragment, problems = parse_fragment(
            json.dumps(value), fields
        )
        self.assertEqual([], problems)
        self.assertEqual(value, fragment)
        value["decorative_confidence"] = 0.99
        _, problems = parse_fragment(json.dumps(value), fields)
        self.assertIn("response_fields_do_not_match_contract", problems)

    def test_cloudflare_1010_is_not_misreported_as_a_bad_secret(self) -> None:
        self.assertEqual(
            "network_policy_blocked",
            classify_http_error(403, "error code: 1010"),
        )
        self.assertEqual(
            "authentication_or_plan_rejected",
            classify_http_error(403, "model not available on plan"),
        )

    def test_featherless_is_drafter_only_with_direct_fallbacks(self) -> None:
        providers = self.policy["providers"]
        self.assertIn("deepseek-ai/DeepSeek-V4-Flash", providers["featherless"]["preferred_models"])
        self.assertEqual("DEEPSEEK_API_KEY", providers["deepseek_direct"]["secret_env"])
        self.assertEqual("KIMI_API_KEY", providers["moonshot_direct"]["secret_env"])
        self.assertFalse(self.policy["safety"]["self_review_satisfies_independence"])


if __name__ == "__main__":
    unittest.main()
