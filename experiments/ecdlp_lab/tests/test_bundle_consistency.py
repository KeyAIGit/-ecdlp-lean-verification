from __future__ import annotations

import unittest
from copy import deepcopy
from pathlib import Path

from experiments.ecdlp_lab.core.canonical import load_json, sha256_file, sha256_json
from experiments.ecdlp_lab.core.contracts import (
    ValidationContext,
    validate_contract,
    validate_cross_record_bundle,
)


VALID_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "contracts" / "valid"
VALID_MANIFEST = VALID_ROOT.parent / "valid_manifest_v1.json"
REPO_ROOT = Path(__file__).resolve().parents[3]
PRIMARY_FIELDS = {
    "campaign_config_v1": "campaign_id",
    "target_vector_v1": "target_vector_id",
    "work_unit_v1": "work_unit_id",
    "method_request_v1": "request_id",
    "method_result_v1": "result_id",
    "telemetry_v1": "telemetry_id",
    "validation_receipt_v1": "validation_id",
    "analysis_summary_v1": "analysis_id",
    "artifact_ref_v1": "artifact_id",
}


def fixture(name: str) -> dict[str, object]:
    value = load_json(VALID_ROOT / name)
    if not isinstance(value, dict):
        raise AssertionError(f"{name} is not a JSON object")
    return value


class CoherentBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.campaign = fixture("campaign_config_v1.json")
        cls.public_target = fixture("target_vector_public_v1.json")
        cls.private_target = fixture("target_vector_private_v1.json")
        cls.work = fixture("work_unit_v1.json")
        cls.request = fixture("method_request_v1.json")
        cls.result = fixture("method_result_v1.json")
        cls.telemetry = fixture("telemetry_v1.json")
        cls.receipt = fixture("validation_receipt_v1.json")
        cls.analysis = fixture("analysis_summary_v1.json")
        manifest = load_json(VALID_MANIFEST)
        cls.bundle_records = []
        record_hashes: dict[str, str] = {}
        for row in manifest["records"]:
            path = REPO_ROOT / row["path"]
            record = load_json(path)
            cls.bundle_records.append(record)
            primary = record[PRIMARY_FIELDS[record["contract_kind"]]]
            record_hashes[primary] = sha256_file(path)
        cls.context = ValidationContext.from_records(
            cls.bundle_records,
            repo_root=REPO_ROOT,
            known_catalog_sha256s={
                cls.public_target["public_payload"]["curve_catalog_sha256"]
            },
            known_target_vector_sha256s={cls.public_target["target_vector_id"]},
            record_sha256s_by_id=record_hashes,
        )

    def test_work_and_attempt_identifiers_are_derived_not_free(self) -> None:
        self.assertEqual(self.work["work_unit_id"], sha256_json(self.work["identity"]))
        expected_attempt = {
            "retry_ordinal": self.work["retry_ordinal"],
            "work_unit_id": self.work["work_unit_id"],
        }
        self.assertEqual(self.work["attempt_id"], sha256_json(expected_attempt))

    def test_work_request_result_and_telemetry_share_one_attempt(self) -> None:
        for record in (self.request, self.result, self.telemetry):
            with self.subTest(contract_kind=record["contract_kind"]):
                self.assertEqual(record["work_unit_id"], self.work["work_unit_id"])
                self.assertEqual(record["attempt_id"], self.work["attempt_id"])

    def test_method_request_matches_work_identity_and_public_vector(self) -> None:
        identity = self.work["identity"]
        public = self.public_target["public_payload"]
        self.assertIsInstance(identity, dict)
        self.assertIsInstance(public, dict)
        for key in (
            "method_id",
            "algorithm_seed",
            "curve_catalog_sha256",
            "curve_fixture_id",
            "public_target_vector_sha256",
        ):
            self.assertEqual(self.request[key], identity[key])
        self.assertEqual(
            self.request["public_target_vector_sha256"],
            self.public_target["target_vector_id"],
        )
        for key in ("generator", "target", "subgroup_order", "subgroup_order_bits"):
            self.assertEqual(self.request[key], public[key])
        curve = self.request["curve"]
        self.assertIsInstance(curve, dict)
        for key in ("curve_id", "field_bits", "field_p", "curve_a", "curve_b"):
            self.assertEqual(curve[key], public[key])

    def test_private_target_receipt_is_linked_but_not_in_method_request(self) -> None:
        private = self.private_target["private_payload"]
        self.assertIsInstance(private, dict)
        self.assertEqual(
            private["public_target_vector_sha256"], self.public_target["target_vector_id"]
        )
        for forbidden in ("expected_scalar", "target_derivation_seed", "private_payload"):
            self.assertNotIn(forbidden, self.request)

    def test_validation_and_analysis_follow_the_same_result_chain(self) -> None:
        self.assertEqual(self.receipt["subject_id"], self.result["result_id"])
        self.assertEqual(self.receipt["subject_contract_kind"], "method_result_v1")
        self.assertIn(
            sha256_json(self.receipt),
            self.analysis["input_validation_receipt_sha256s"],
        )
        self.assertEqual(self.analysis["campaign_id"], self.campaign["campaign_id"])

    def test_semantic_cross_record_validator_accepts_the_coherent_bundle(self) -> None:
        self.assertEqual(
            validate_cross_record_bundle(self.bundle_records, self.context),
            [],
        )

    def test_cross_record_validator_rejects_attempt_drift(self) -> None:
        mutated = deepcopy(self.bundle_records)
        result = next(
            record for record in mutated if record["contract_kind"] == "method_result_v1"
        )
        result["attempt_id"] = "0" * 64
        codes = {
            issue.code for issue in validate_cross_record_bundle(mutated, self.context)
        }
        self.assertIn("cross.result.request", codes)

    def test_campaign_count_must_equal_full_matrix_product(self) -> None:
        mutated = deepcopy(self.campaign)
        mutated["expected_work_unit_count"] = 2
        codes = {issue.code for issue in validate_contract(mutated, self.context)}
        self.assertIn("contract.campaign.work_count", codes)

    def test_duplicate_public_target_identifier_is_rejected(self) -> None:
        mutated = deepcopy(self.bundle_records)
        public = next(
            record
            for record in mutated
            if record["contract_kind"] == "target_vector_v1"
            and record["branch"] == "public"
        )
        mutated.append(deepcopy(public))
        codes = {
            issue.code for issue in validate_cross_record_bundle(mutated, self.context)
        }
        self.assertIn("cross.target.duplicate_public", codes)


if __name__ == "__main__":
    unittest.main()
