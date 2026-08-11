from __future__ import annotations

import unittest
from copy import deepcopy
from pathlib import Path

from experiments.ecdlp_lab.core.canonical import load_json, sha256_file, sha256_json
from experiments.ecdlp_lab.core.contracts import (
    PRIMARY_ID_FIELDS,
    ValidationContext,
    derive_campaign_id,
    validate_contract,
    validate_cross_record_bundle,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
VALID_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "contracts" / "valid"
VALID_MANIFEST = VALID_ROOT.parent / "valid_manifest_v1.json"


def load_bundle() -> list[dict[str, object]]:
    manifest = load_json(VALID_MANIFEST)
    return [load_json(REPO_ROOT / row["path"]) for row in manifest["records"]]


def one(records: list[dict[str, object]], kind: str, *, branch: str | None = None) -> dict[str, object]:
    return next(
        record
        for record in records
        if record.get("contract_kind") == kind
        and (branch is None or record.get("branch") == branch)
    )


def trusted_context(records: list[dict[str, object]]) -> ValidationContext:
    public = one(records, "target_vector_v1", branch="public")
    payload = public["public_payload"]
    manifest = load_json(VALID_MANIFEST)
    raw_hashes: dict[str, str] = {}
    for row in manifest["records"]:
        path = REPO_ROOT / row["path"]
        record = load_json(path)
        primary = record[PRIMARY_ID_FIELDS[record["contract_kind"]]]
        raw_hashes[primary] = sha256_file(path)
    return ValidationContext.from_records(
        records,
        repo_root=REPO_ROOT,
        known_catalog_sha256s={payload["curve_catalog_sha256"]},
        known_target_vector_sha256s={public["target_vector_id"]},
        record_sha256s_by_id=raw_hashes,
    )


class SecurityRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.records = load_bundle()
        self.context = trusted_context(self.records)

    def test_bundle_cannot_authorize_its_own_catalog_or_target(self) -> None:
        self_derived = ValidationContext.from_records(self.records, repo_root=REPO_ROOT)
        issues = validate_cross_record_bundle(self.records, self_derived)
        codes = {issue.code for issue in issues}
        self.assertIn("contract.catalog.unknown", codes)
        self.assertIn("contract.target_vector.unknown", codes)
        self.assertIn("cross.artifact.hash_context", codes)

    def test_semantic_hash_links_are_never_optional(self) -> None:
        mutated = deepcopy(self.records)
        zero = "0" * 64
        one(mutated, "method_result_v1")["method_request_sha256"] = zero
        receipt = one(mutated, "validation_receipt_v1")
        receipt["subject_sha256"] = zero
        receipt["private_target_receipt_sha256"] = zero
        one(mutated, "analysis_summary_v1")["input_validation_receipt_sha256s"] = [zero]
        codes = {
            issue.code for issue in validate_cross_record_bundle(mutated, self.context)
        }
        self.assertIn("cross.result.request_hash", codes)
        self.assertIn("cross.receipt.subject_hash", codes)
        self.assertIn("cross.receipt.private_target", codes)
        self.assertIn("cross.analysis.receipts", codes)

    def test_campaign_and_target_ids_are_derived(self) -> None:
        campaign = deepcopy(one(self.records, "campaign_config_v1"))
        campaign["budgets"]["max_steps"] += 1
        self.assertIn(
            "contract.campaign.digest",
            {issue.code for issue in validate_contract(campaign, self.context)},
        )
        target = deepcopy(one(self.records, "target_vector_v1", branch="public"))
        target["public_payload"]["target"] = [1, 2]
        self.assertIn(
            "contract.target.digest",
            {issue.code for issue in validate_contract(target, self.context)},
        )

    def test_trailing_newline_cannot_satisfy_anchored_digest_pattern(self) -> None:
        campaign = deepcopy(one(self.records, "campaign_config_v1"))
        campaign["campaign_id"] = "a" * 64 + "\n"
        self.assertIn(
            "schema.pattern",
            {issue.code for issue in validate_contract(campaign, self.context)},
        )

    def test_work_cannot_self_validate_or_raise_campaign_budgets(self) -> None:
        mutated = deepcopy(self.records)
        work = one(mutated, "work_unit_v1")
        identity = work["identity"]
        identity["validator_implementation_sha256"] = identity[
            "method_implementation_sha256"
        ]
        identity["budgets"]["max_steps"] += 1
        work["work_unit_id"] = sha256_json(identity)
        work["attempt_id"] = sha256_json(
            {
                "retry_ordinal": work["retry_ordinal"],
                "work_unit_id": work["work_unit_id"],
            }
        )
        codes = {
            issue.code for issue in validate_cross_record_bundle(mutated, self.context)
        }
        self.assertIn("contract.work.self_validator", codes)
        self.assertIn("cross.work.budgets", codes)

    def test_request_budgets_must_match_work(self) -> None:
        mutated = deepcopy(self.records)
        request = one(mutated, "method_request_v1")
        request["budgets"]["max_steps"] += 1
        self.assertIn(
            "cross.request.identity",
            {issue.code for issue in validate_cross_record_bundle(mutated, self.context)},
        )

    def test_repetition_axis_requires_complete_cartesian_coverage(self) -> None:
        mutated = deepcopy(self.records)
        campaign = one(mutated, "campaign_config_v1")
        campaign["matrix"]["repetitions"] = 2
        campaign["expected_work_unit_count"] = 2
        campaign["campaign_id"] = derive_campaign_id(campaign)
        campaign["provenance"]["config_sha256"] = campaign["campaign_id"]
        codes = {
            issue.code for issue in validate_cross_record_bundle(mutated, self.context)
        }
        self.assertIn("cross.campaign.coverage", codes)

    def test_failed_relation_cannot_be_passed_or_retained(self) -> None:
        receipt = deepcopy(one(self.records, "validation_receipt_v1"))
        receipt["candidate_relation_valid"] = False
        receipt["checks"][0]["status"] = "failed"
        codes = {issue.code for issue in validate_contract(receipt, self.context)}
        self.assertIn("contract.validation.relation", codes)
        self.assertIn("contract.validation.checks", codes)

    def test_result_is_not_directly_retainable_and_artifact_needs_receipt(self) -> None:
        result = deepcopy(one(self.records, "method_result_v1"))
        result["retainable"] = True
        self.assertIn(
            "contract.result.retainable",
            {issue.code for issue in validate_contract(result, self.context)},
        )

        mutated = deepcopy(self.records)
        one(mutated, "artifact_ref_v1")["retainable"] = True
        self.assertIn(
            "cross.retention.receipt",
            {issue.code for issue in validate_cross_record_bundle(mutated, self.context)},
        )

    def test_success_scalar_must_be_canonical_modulo_subgroup_order(self) -> None:
        mutated = deepcopy(self.records)
        request = one(mutated, "method_request_v1")
        result = one(mutated, "method_result_v1")
        receipt = one(mutated, "validation_receipt_v1")
        result["candidate_scalar"] = request["subgroup_order"]
        receipt["candidate_scalar"] = result["candidate_scalar"]
        receipt["subject_sha256"] = sha256_json(result)
        analysis = one(mutated, "analysis_summary_v1")
        analysis["input_validation_receipt_sha256s"] = [sha256_json(receipt)]
        self.assertIn(
            "cross.result.scalar_range",
            {issue.code for issue in validate_cross_record_bundle(mutated, self.context)},
        )


if __name__ == "__main__":
    unittest.main()
