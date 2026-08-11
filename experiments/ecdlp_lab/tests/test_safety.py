from __future__ import annotations

import unittest

from experiments.ecdlp_lab.core.safety import (
    SECP256K1_FIELD_P,
    SECP256K1_SUBGROUP_N,
    validate_safety,
)


def boundary_record(contract_kind: str = "method_request_v1") -> dict[str, object]:
    return {
        "schema_version": 1,
        "record_kind": "lab_engineering_fixture",
        "contract_kind": contract_kind,
        "internal_classification": "engineering_only",
        "framework_authorization_class": "fixture",
        "hypothesis_id": None,
        "candidate_id": None,
        "authorization_id": None,
        "native_research_outcome": False,
        "route_effect": "none",
        "retention_class": "engineering_only",
        "retainable": False,
    }


class HardSafetyBoundaryTests(unittest.TestCase):
    @staticmethod
    def codes(record: object) -> set[str]:
        return {issue.code for issue in validate_safety(record)}

    def test_33_bit_subgroup_is_rejected_even_without_schema_dispatch(self) -> None:
        record = boundary_record()
        record.update(
            {
                "curve": {
                    "field_p": 65537,
                    "field_bits": 17,
                    "curve_a": 2,
                    "curve_b": 3,
                },
                "generator": [1, 2],
                "target": [3, 4],
                "subgroup_order": 1 << 32,
                "subgroup_order_bits": 33,
            }
        )
        self.assertIn("safety.subgroup_bits", self.codes(record))

    def test_exact_secp256k1_field_and_order_are_both_rejected(self) -> None:
        record = boundary_record()
        record.update(
            {
                "curve": {
                    "field_p": SECP256K1_FIELD_P,
                    "field_bits": 256,
                    "curve_a": 0,
                    "curve_b": 7,
                },
                "generator": [1, 2],
                "target": [3, 4],
                "subgroup_order": SECP256K1_SUBGROUP_N,
                "subgroup_order_bits": 256,
            }
        )
        issues = validate_safety(record)
        secp_paths = {issue.path for issue in issues if issue.code == "safety.secp256k1"}
        self.assertEqual(
            secp_paths,
            {"$.curve.field_p", "$.subgroup_order"},
        )
        self.assertIn("safety.field_bits", {issue.code for issue in issues})
        self.assertIn("safety.subgroup_bits", {issue.code for issue in issues})

    def test_authorization_bearing_identifiers_fail_the_lab_boundary(self) -> None:
        for key in ("hypothesis_id", "candidate_id", "authorization_id"):
            with self.subTest(key=key):
                record = boundary_record()
                record[key] = "NOT-ALLOWED"
                issues = validate_safety(record)
                self.assertTrue(
                    any(issue.code == "safety.boundary" and issue.path == f"$.{key}" for issue in issues)
                )

    def test_dirty_record_cannot_claim_retainable(self) -> None:
        record = boundary_record()
        record["retainable"] = True
        record["provenance"] = {
            "source_tree_clean": False,
            "diff_sha256": "d" * 64,
        }
        self.assertIn("safety.dirty_retainable", self.codes(record))


if __name__ == "__main__":
    unittest.main()
