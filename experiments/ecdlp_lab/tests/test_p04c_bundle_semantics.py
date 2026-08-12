from __future__ import annotations

import unittest
from copy import deepcopy
from pathlib import Path

from experiments.ecdlp_lab.core.canonical import load_json, sha256_json
from experiments.ecdlp_lab.core.contracts import ValidationContext, validate_cross_record_bundle


REPO_ROOT = Path(__file__).resolve().parents[3]
VALID_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "contracts" / "valid"
NAMES = (
    "campaign_config_v1.json",
    "target_vector_public_v1.json",
    "target_vector_private_v1.json",
    "work_unit_v1.json",
    "method_request_v1.json",
    "method_result_v1.json",
    "validation_receipt_v1.json",
)


def load_records() -> list[dict[str, object]]:
    return [load_json(VALID_ROOT / name) for name in NAMES]


def one(records: list[dict[str, object]], kind: str) -> dict[str, object]:
    return next(record for record in records if record["contract_kind"] == kind)


def context(records: list[dict[str, object]]) -> ValidationContext:
    public = next(
        record
        for record in records
        if record["contract_kind"] == "target_vector_v1"
        and record["branch"] == "public"
    )
    return ValidationContext.from_records(
        records,
        known_catalog_sha256s={public["public_payload"]["curve_catalog_sha256"]},
        known_target_vector_sha256s={public["target_vector_id"]},
        verify_artifacts=False,
    )


class ReceiptOutcomeSemanticsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.records = load_records()
        self.context = context(self.records)

    def codes(self, records: list[dict[str, object]]) -> set[str]:
        return {
            issue.code for issue in validate_cross_record_bundle(records, self.context)
        }

    def test_legacy_success_receipt_remains_compatible(self) -> None:
        self.assertEqual(validate_cross_record_bundle(self.records, self.context), [])

    def test_explicit_success_uses_exact_three_decisive_checks(self) -> None:
        mutated = deepcopy(self.records)
        receipt = one(mutated, "validation_receipt_v1")
        receipt["subject_status"] = "success"
        receipt["checks"].append(
            {
                "check_id": "private_target_binding_v1",
                "status": "passed",
                "detail": "Authenticated public/private target pair is bound.",
            }
        )
        self.assertNotIn("cross.receipt.decisive_checks", self.codes(mutated))
        receipt["checks"].append(
            {"check_id": "extra_check_v1", "status": "passed", "detail": "extra"}
        )
        self.assertIn("cross.receipt.decisive_checks", self.codes(mutated))

    def test_explicit_null_status_is_not_the_legacy_absent_status_branch(self) -> None:
        mutated = deepcopy(self.records)
        receipt = one(mutated, "validation_receipt_v1")
        receipt["subject_status"] = None
        self.assertIn("cross.receipt.subject_status", self.codes(mutated))

    def test_non_success_requires_status_null_candidate_and_exact_five_checks(self) -> None:
        mutated = deepcopy(self.records)
        result = one(mutated, "method_result_v1")
        result["status"] = "bounded_failure"
        result["candidate_scalar"] = None
        result["failure"] = {
            "code": "step_budget_exhausted",
            "detail": "bounded test outcome",
        }
        receipt = one(mutated, "validation_receipt_v1")
        receipt["subject_status"] = "bounded_failure"
        receipt["candidate_scalar"] = None
        receipt["candidate_relation_valid"] = None
        receipt["subject_sha256"] = sha256_json(result)
        receipt["checks"] = [
            {"check_id": check_id, "status": "passed", "detail": "checked"}
            for check_id in (
                "subject_status_binding_v1",
                "public_input_validation_v1",
                "counters_binding_v1",
                "private_target_binding_v1",
                "provenance_binding_v1",
            )
        ]
        self.assertNotIn("cross.receipt.subject_status", self.codes(mutated))
        self.assertNotIn("cross.receipt.non_success_candidate", self.codes(mutated))
        receipt.pop("subject_status")
        self.assertIn("cross.receipt.subject_status", self.codes(mutated))

    def test_validator_disagreement_cannot_be_passed(self) -> None:
        mutated = deepcopy(self.records)
        receipt = one(mutated, "validation_receipt_v1")
        receipt["candidate_relation_valid"] = False
        self.assertIn("cross.receipt.relation", self.codes(mutated))

    def test_receipt_provenance_must_equal_result_work_and_campaign(self) -> None:
        mutated = deepcopy(self.records)
        receipt = one(mutated, "validation_receipt_v1")
        receipt["provenance"] = deepcopy(receipt["provenance"])
        receipt["provenance"]["source_snapshot_sha256"] = "f" * 64
        self.assertIn("cross.receipt.provenance", self.codes(mutated))

    def test_failure_status_detail_and_counters_are_semantically_bounded(self) -> None:
        mutated = deepcopy(self.records)
        result = one(mutated, "method_result_v1")
        receipt = one(mutated, "validation_receipt_v1")
        result["status"] = "internal_error"
        result["candidate_scalar"] = None
        result["failure"] = {
            "code": "step_budget_exhausted",
            "detail": "attacker supplied detail",
        }
        counters = result["counters"]
        counters["offline_setup"]["nontrivial_additions"] = (
            counters["offline_setup"]["group_law_invocations"] + 1
        )
        counters["noninvertible_collisions"] = counters["collisions"] + 1
        counters["estimated_algorithmic_table_bytes"] = (
            one(mutated, "method_request_v1")["budgets"]["max_memory_bytes"] + 1
        )
        receipt["subject_sha256"] = sha256_json(result)
        codes = self.codes(mutated)
        self.assertIn("cross.result.failure", codes)
        self.assertIn("cross.result.counters", codes)
        self.assertIn("cross.result.budgets", codes)

    def test_private_receipt_must_bind_the_work_public_target(self) -> None:
        mutated = deepcopy(self.records)
        private = next(
            record
            for record in mutated
            if record["contract_kind"] == "target_vector_v1"
            and record["branch"] == "private_validator_only"
        )
        private["private_payload"]["public_target_vector_sha256"] = "e" * 64
        private["target_vector_id"] = sha256_json(private["private_payload"])
        receipt = one(mutated, "validation_receipt_v1")
        receipt["private_target_receipt_sha256"] = private["target_vector_id"]
        self.assertIn("cross.receipt.private_target_binding", self.codes(mutated))

    def test_success_candidate_must_match_private_target_authority(self) -> None:
        mutated = deepcopy(self.records)
        private = next(
            record
            for record in mutated
            if record["contract_kind"] == "target_vector_v1"
            and record["branch"] == "private_validator_only"
        )
        private["private_payload"]["expected_scalar"] = 2
        private["target_vector_id"] = sha256_json(private["private_payload"])
        receipt = one(mutated, "validation_receipt_v1")
        receipt["private_target_receipt_sha256"] = private["target_vector_id"]
        self.assertIn("cross.receipt.private_target_binding", self.codes(mutated))


if __name__ == "__main__":
    unittest.main()
