from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from experiments.ecdlp_lab.core.contract_validation import (
    ContractValidationError,
    build_record,
    compute_attempt_id,
    compute_identity,
    compute_record_sha256,
    load_registry,
    validate_record,
)


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


class ContractValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = load_registry(FIXTURES / "registry.json")
        cls.valid = json.loads((FIXTURES / "valid_records.json").read_text())
        cls.invalid = json.loads((FIXTURES / "invalid_records.json").read_text())

    def test_all_nine_contract_families_validate(self) -> None:
        self.assertEqual(len(self.valid), 9)
        for name, record in self.valid.items():
            with self.subTest(contract=name):
                validate_record(record, self.registry)

    def test_all_adversarial_records_are_rejected(self) -> None:
        for case in self.invalid:
            with self.subTest(case=case["name"]):
                with self.assertRaisesRegex(ContractValidationError, case["expected_error"]):
                    validate_record(case["record"], self.registry)

    def test_retry_changes_attempt_not_work_unit(self) -> None:
        base = self.valid["work_unit"]
        payload = copy.deepcopy(base["payload"])
        payload.pop("work_unit_id")
        payload.pop("attempt_id")
        payload["retry_index"] = 7
        retry = build_record("work_unit", payload, retainable=True)
        self.assertEqual(base["payload"]["work_unit_id"], retry["payload"]["work_unit_id"])
        self.assertNotEqual(base["payload"]["attempt_id"], retry["payload"]["attempt_id"])
        self.assertEqual(
            retry["payload"]["attempt_id"],
            compute_attempt_id(retry["payload"]["work_unit_id"], 7),
        )
        validate_record(retry, self.registry)

    def test_code_change_changes_work_unit(self) -> None:
        base = self.valid["work_unit"]
        payload = copy.deepcopy(base["payload"])
        payload.pop("work_unit_id")
        payload.pop("attempt_id")
        payload["source"]["commit"] = "2" * 40
        changed = build_record("work_unit", payload, retainable=True)
        self.assertNotEqual(base["payload"]["work_unit_id"], changed["payload"]["work_unit_id"])
        validate_record(changed, self.registry)

    def test_identity_and_record_digest_are_recomputable(self) -> None:
        for name, record in self.valid.items():
            with self.subTest(contract=name):
                identity_field = {
                    "campaign_config": "campaign_id",
                    "target_vector": "target_vector_id",
                    "work_unit": "work_unit_id",
                    "method_request": "request_id",
                    "method_result": "result_id",
                    "telemetry": "telemetry_id",
                    "validation_receipt": "validation_receipt_id",
                    "analysis_summary": "analysis_summary_id",
                    "artifact_ref": "artifact_ref_id",
                }[name]
                self.assertEqual(record["payload"][identity_field], compute_identity(record))
                self.assertEqual(record["record_sha256"], compute_record_sha256(record))


if __name__ == "__main__":
    unittest.main()
