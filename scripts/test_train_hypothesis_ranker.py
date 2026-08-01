#!/usr/bin/env python3
"""Regression tests for deterministic ranker training."""

from __future__ import annotations

import copy
import unittest

from hypothesis_ranker import SPEC_PATH, load_json
from train_hypothesis_ranker import train_model


def synthetic_labels(*, separable: bool) -> list[dict[str, object]]:
    spec = load_json(SPEC_PATH)
    names = spec["feature_contract"]["numeric"]
    labels: list[dict[str, object]] = []
    for family_index in range(5):
        for item_index in range(8):
            label = 1 if item_index >= 4 else 0
            value = float(5 if label else 1) if separable else 3.0
            labels.append(
                {
                    "label_id": f"SYN-{family_index}-{item_index}",
                    "label_ids": [f"SYN-{family_index}-{item_index}"],
                    "review_record_sha256": f"{family_index:02x}{item_index:02x}" * 16,
                    "semantic_signature_sha256": f"{family_index:02x}{item_index:02x}" * 16,
                    "candidate_version_sha256": f"{family_index:02x}{item_index:02x}" * 16,
                    "family": f"family-{family_index}",
                    "binary_label": label,
                    "training_eligible": True,
                    "features": {name: value for name in names},
                }
            )
    return labels


class HypothesisRankerTrainingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = load_json(SPEC_PATH)

    def test_separable_fixture_trains_deterministically(self) -> None:
        labels = synthetic_labels(separable=True)
        first = train_model(labels, self.spec)
        second = train_model(copy.deepcopy(labels), self.spec)
        self.assertEqual(first, second)
        self.assertTrue(first["trained"])
        self.assertGreaterEqual(first["validation"]["balanced_accuracy"], 0.95)
        self.assertGreaterEqual(first["validation"]["auc"], 0.95)
        self.assertFalse(first["selection_influence"])
        self.assertFalse(first["authorization_capability"])

    def test_uninformative_fixture_fails_validation(self) -> None:
        with self.assertRaisesRegex(ValueError, "validation gate failed"):
            train_model(synthetic_labels(separable=False), self.spec)


if __name__ == "__main__":
    unittest.main()
