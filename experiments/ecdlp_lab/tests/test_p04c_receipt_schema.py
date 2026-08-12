from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest

from experiments.ecdlp_lab.core.canonical import load_json
from experiments.ecdlp_lab.core.contracts import ValidationContext, validate_contract
from experiments.ecdlp_lab.core.schema import schema_definition_issues, validate_schema


LAB_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = LAB_ROOT.parents[1]
SCHEMA_PATH = LAB_ROOT / "contracts" / "validation_receipt_v1.schema.json"
FIXTURE_PATH = (
    LAB_ROOT
    / "fixtures"
    / "contracts"
    / "valid"
    / "validation_receipt_v1.json"
)


def non_success_receipt(status: str = "bounded_failure") -> dict[str, object]:
    receipt = deepcopy(load_json(FIXTURE_PATH))
    receipt.update(
        {
            "subject_status": status,
            "candidate_scalar": None,
            "candidate_relation_valid": None,
            "passed": True,
            "checks": [
                {
                    "check_id": "subject_status_binding_v1",
                    "status": "passed",
                    "detail": "The bounded public status binds the method result.",
                },
                {
                    "check_id": "public_input_validation_v1",
                    "status": "passed",
                    "detail": "The public method input was independently validated.",
                },
                {
                    "check_id": "counters_binding_v1",
                    "status": "passed",
                    "detail": "The bounded method counters were validated.",
                },
                {
                    "check_id": "private_target_binding_v1",
                    "status": "passed",
                    "detail": "The target identities remain digest-bound.",
                },
                {
                    "check_id": "provenance_binding_v1",
                    "status": "passed",
                    "detail": "Producer and validator provenance is bound.",
                },
            ],
        }
    )
    return receipt


class P04CReceiptSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = load_json(SCHEMA_PATH)
        cls.legacy = load_json(FIXTURE_PATH)
        cls.context = ValidationContext(repo_root=REPO_ROOT, verify_artifacts=False)

    def test_schema_is_supported_and_legacy_p01_receipt_remains_valid(self) -> None:
        self.assertEqual(schema_definition_issues(self.schema), [])
        self.assertNotIn("subject_status", self.legacy)
        self.assertEqual(validate_schema(self.legacy, self.schema), [])
        self.assertEqual(validate_contract(self.legacy, self.context), [])

    def test_explicit_success_requires_integer_and_passed_relation(self) -> None:
        receipt = deepcopy(self.legacy)
        receipt["subject_status"] = "success"
        self.assertEqual(validate_schema(receipt, self.schema), [])

        no_candidate = deepcopy(receipt)
        no_candidate["candidate_scalar"] = None
        self.assertNotEqual(validate_schema(no_candidate, self.schema), [])

        disagreement_claimed_passed = deepcopy(receipt)
        disagreement_claimed_passed["candidate_relation_valid"] = False
        self.assertNotEqual(
            validate_schema(disagreement_claimed_passed, self.schema), []
        )

    def test_bounded_and_internal_non_success_can_be_independently_passed(self) -> None:
        for status in ("bounded_failure", "invalid_request", "internal_error"):
            with self.subTest(status=status):
                receipt = non_success_receipt(status)
                self.assertEqual(validate_schema(receipt, self.schema), [])
                self.assertEqual(validate_contract(receipt, self.context), [])

                with_candidate = deepcopy(receipt)
                with_candidate["candidate_scalar"] = 0
                self.assertNotEqual(validate_schema(with_candidate, self.schema), [])

                with_relation = deepcopy(receipt)
                with_relation["candidate_relation_valid"] = True
                self.assertNotEqual(validate_schema(with_relation, self.schema), [])

    def test_non_success_pass_requires_every_status_provenance_check_to_pass(self) -> None:
        receipt = non_success_receipt()
        receipt["checks"][1]["status"] = "failed"
        self.assertNotEqual(validate_schema(receipt, self.schema), [])
        self.assertIn(
            "contract.validation.checks",
            {issue.code for issue in validate_contract(receipt, self.context)},
        )

        no_provenance = non_success_receipt()
        no_provenance["provenance_valid"] = False
        self.assertNotEqual(validate_schema(no_provenance, self.schema), [])

    def test_success_validator_disagreement_is_a_failed_receipt(self) -> None:
        receipt = deepcopy(self.legacy)
        receipt.update(
            {
                "subject_status": "success",
                "candidate_relation_valid": False,
                "passed": False,
                "retention_decision": "reject",
            }
        )
        receipt["checks"][0]["status"] = "failed"
        self.assertEqual(validate_schema(receipt, self.schema), [])

        receipt["passed"] = True
        self.assertNotEqual(validate_schema(receipt, self.schema), [])

    def test_non_method_receipt_cannot_claim_a_method_status(self) -> None:
        receipt = deepcopy(self.legacy)
        receipt.update(
            {
                "subject_contract_kind": "artifact_ref_v1",
                "subject_status": "bounded_failure",
                "candidate_scalar": None,
                "candidate_relation_valid": None,
                "private_target_receipt_sha256": None,
            }
        )
        self.assertNotEqual(validate_schema(receipt, self.schema), [])

        explicit_null = deepcopy(self.legacy)
        explicit_null["subject_status"] = None
        self.assertNotEqual(validate_schema(explicit_null, self.schema), [])


if __name__ == "__main__":
    unittest.main()
