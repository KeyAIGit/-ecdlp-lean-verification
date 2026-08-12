from __future__ import annotations

import unittest
from copy import deepcopy
from pathlib import Path

from experiments.ecdlp_lab.core.canonical import load_json, sha256_json
from experiments.ecdlp_lab.core.contracts import (
    ValidationContext,
    derive_campaign_id,
    validate_cross_record_bundle,
)


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
    "analysis_summary_v1.json",
)


def load_records() -> list[dict[str, object]]:
    return [load_json(VALID_ROOT / name) for name in NAMES]


def one(records: list[dict[str, object]], kind: str) -> dict[str, object]:
    return next(record for record in records if record["contract_kind"] == kind)


def context(
    records: list[dict[str, object]], *, trusted_receipts: set[str] | None = None
) -> ValidationContext:
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
        known_validation_receipt_sha256s=trusted_receipts or (),
        verify_artifacts=False,
    )


def _attempt_id(work_id: str) -> str:
    return sha256_json({"retry_ordinal": 0, "work_unit_id": work_id})


def _request_id(work_id: str, attempt_id: str) -> str:
    return sha256_json(
        {
            "attempt_id": attempt_id,
            "contract_kind": "method_request_v1",
            "work_unit_id": work_id,
        }
    )


def _result_id(work_id: str, attempt_id: str, request_hash: str) -> str:
    return sha256_json(
        {
            "attempt_id": attempt_id,
            "contract_kind": "method_result_v1",
            "method_request_sha256": request_hash,
            "work_unit_id": work_id,
        }
    )


def equal_success_bundle() -> tuple[list[dict[str, object]], ValidationContext]:
    records = load_records()
    campaign = one(records, "campaign_config_v1")
    public = next(
        record
        for record in records
        if record["contract_kind"] == "target_vector_v1"
        and record["branch"] == "public"
    )
    private = next(
        record
        for record in records
        if record["contract_kind"] == "target_vector_v1"
        and record["branch"] == "private_validator_only"
    )
    base_work = one(records, "work_unit_v1")
    base_request = one(records, "method_request_v1")
    base_result = one(records, "method_result_v1")
    base_receipt = one(records, "validation_receipt_v1")
    analysis = one(records, "analysis_summary_v1")

    campaign["matrix"]["algorithm_seeds"] = [7, 8]
    campaign["expected_work_unit_count"] = 2
    campaign["campaign_id"] = derive_campaign_id(campaign)
    campaign["provenance"]["config_sha256"] = campaign["campaign_id"]
    campaign_hash = sha256_json(campaign)

    chains: list[dict[str, object]] = []
    receipts: list[dict[str, object]] = []
    for seed in (7, 8):
        work = deepcopy(base_work)
        work["campaign_id"] = campaign["campaign_id"]
        work["provenance"] = deepcopy(campaign["provenance"])
        work["identity"]["campaign_config_sha256"] = campaign_hash
        work["identity"]["algorithm_seed"] = seed
        work["work_unit_id"] = sha256_json(work["identity"])
        work["attempt_id"] = _attempt_id(work["work_unit_id"])

        request = deepcopy(base_request)
        request["provenance"] = deepcopy(campaign["provenance"])
        request["work_unit_id"] = work["work_unit_id"]
        request["attempt_id"] = work["attempt_id"]
        request["algorithm_seed"] = seed
        request["request_id"] = _request_id(work["work_unit_id"], work["attempt_id"])

        result = deepcopy(base_result)
        result["provenance"] = deepcopy(campaign["provenance"])
        result["work_unit_id"] = work["work_unit_id"]
        result["attempt_id"] = work["attempt_id"]
        result["method_request_sha256"] = sha256_json(request)
        result["result_id"] = _result_id(
            work["work_unit_id"], work["attempt_id"], result["method_request_sha256"]
        )

        receipt = deepcopy(base_receipt)
        receipt["provenance"] = deepcopy(campaign["provenance"])
        receipt["subject_status"] = "success"
        receipt["subject_id"] = result["result_id"]
        receipt["subject_sha256"] = sha256_json(result)
        receipt["checks"] = [
            {
                "check_id": check_id,
                "status": "passed",
                "detail": "independent check passed",
            }
            for check_id in (
                "candidate_relation_v1",
                "private_target_binding_v1",
                "provenance_binding_v1",
            )
        ]
        receipt["validation_id"] = sha256_json(
            {"result_id": result["result_id"], "validator": "lab_ec_oracle_v1"}
        )
        chains.extend((work, request, result))
        receipts.append(receipt)

    payload = public["public_payload"]
    seed_digest = sha256_json([7, 8])
    base_comparison = analysis["comparisons"][0]
    comparison_rows = []
    for success_target in ("0.50", "0.95"):
        row = deepcopy(base_comparison)
        row["full_cost"]["measurement_status"] = "not_measured_v1"
        for field in (
            "online_cpu_hours_decimal",
            "online_gpu_hours_decimal",
            "offline_cpu_hours_decimal",
            "offline_gpu_hours_decimal",
            "storage_gb_decimal",
            "money_usd_decimal",
            "implementation_hours_decimal",
            "reviewer_hours_decimal",
        ):
            row["full_cost"][field] = None
        row["successes"] = 2
        row.update(
            {
                "public_target_vector_sha256": public["target_vector_id"],
                "curve_fixture_id": payload["curve_fixture_id"],
                "subgroup_order": payload["subgroup_order"],
                "log2_subgroup_order_decimal": "12.508537595347",
                "success_target_decimal": success_target,
                "independent_seed_count": 2,
                "algorithm_seed_set_sha256": seed_digest,
                "equal_success_status": "reached",
                "equal_success_attempts": 1,
                "expected_attempts_decimal": "1",
                "conservative_normalized_group_operations_decimal": "101",
                "optimistic_normalized_group_operations_decimal": "101",
                "equal_success_full_cost": deepcopy(row["full_cost"]),
                "clustered_uncertainty": {
                    "method": "delete_one_cluster_envelope_v1",
                    "cluster_count": 2,
                    "lower_decimal": "101",
                    "upper_decimal": "101",
                },
            }
        )
        comparison_rows.append(row)

    base_fit = analysis["model_fits"][0]
    model_rows = []
    for success_target in ("0.50", "0.95"):
        row = deepcopy(base_fit)
        row.update(
            {
                "method_id": "bsgs_v1",
                "success_target_decimal": success_target,
                "clustered_uncertainty": {
                    "method": "delete_one_cluster_envelope_v1",
                    "cluster_count": 2,
                    "lower_decimal": "0",
                    "upper_decimal": "0",
                },
                "residuals": [
                    {
                        "curve_fixture_id": payload["curve_fixture_id"],
                        "subgroup_order": payload["subgroup_order"],
                        "observed_log2_cost_decimal": "6",
                        "predicted_log2_cost_decimal": "6",
                        "residual_decimal": "0",
                    }
                ],
                "leave_one_size_out": [
                    {
                        "omitted_subgroup_order": payload["subgroup_order"],
                        "status": "insufficient_data",
                        "alpha_decimal": None,
                        "beta_decimal": None,
                    }
                ],
            }
        )
        model_rows.append(row)

    analysis["provenance"] = deepcopy(campaign["provenance"])
    analysis["campaign_id"] = campaign["campaign_id"]
    analysis["input_validation_receipt_sha256s"] = [
        sha256_json(receipt) for receipt in receipts
    ]
    analysis["analysis_protocol_id"] = "equal_success_scaling_v1"
    analysis["analysis_policies"] = {
        "success_estimation": "conservative_empirical_v1",
        "censoring": "exclude_primary_fit_report_sensitivity_v1",
        "unreachable": "null_cost_with_budget_bound_v1",
        "uncertainty": "delete_one_cluster_envelope_v1",
        "clustering": "curve_and_algorithm_seed_v1",
        "residuals": "log2_cost_v1",
        "outliers": "report_no_silent_drop_v1",
        "cross_validation": "leave_one_distinct_size_out_v1",
    }
    analysis["comparisons"] = comparison_rows
    analysis["model_fits"] = model_rows
    bundle = [campaign, public, private, *chains, *receipts, analysis]
    trusted = context(
        bundle,
        trusted_receipts=set(analysis["input_validation_receipt_sha256s"]),
    )
    return bundle, trusted


class AnalysisCampaignAffiliationTests(unittest.TestCase):
    def test_exact_equal_success_protocol_bundle_is_coherent(self) -> None:
        records, trusted = equal_success_bundle()
        self.assertEqual(validate_cross_record_bundle(records, trusted), [])

    def test_analysis_rejects_receipt_from_a_different_existing_campaign(self) -> None:
        records = load_records()
        first_campaign = one(records, "campaign_config_v1")
        second_campaign = deepcopy(first_campaign)
        second_campaign["budgets"]["max_steps"] += 1
        second_campaign["campaign_id"] = derive_campaign_id(second_campaign)
        second_campaign["provenance"]["config_sha256"] = second_campaign[
            "campaign_id"
        ]
        records.append(second_campaign)
        analysis = one(records, "analysis_summary_v1")
        analysis["campaign_id"] = second_campaign["campaign_id"]
        codes = {
            issue.code
            for issue in validate_cross_record_bundle(records, context(records))
        }
        self.assertIn("cross.analysis.receipt_campaign", codes)

    def test_equal_success_protocol_fails_closed_without_trusted_receipt_index(self) -> None:
        records = load_records()
        analysis = one(records, "analysis_summary_v1")
        analysis["analysis_protocol_id"] = "equal_success_scaling_v1"
        # The schema agent owns full protocol shapes; this test isolates authority.
        codes = {
            issue.code
            for issue in validate_cross_record_bundle(records, context(records))
        }
        self.assertIn("cross.analysis.receipt_authority", codes)

    def test_equal_success_receipt_authority_is_external_not_bundle_derived(self) -> None:
        records = load_records()
        analysis = one(records, "analysis_summary_v1")
        analysis["analysis_protocol_id"] = "equal_success_scaling_v1"
        receipt_hash = sha256_json(one(records, "validation_receipt_v1"))
        trusted = context(records, trusted_receipts={receipt_hash})
        codes = {
            issue.code for issue in validate_cross_record_bundle(records, trusted)
        }
        self.assertNotIn("cross.analysis.receipt_authority", codes)

    def test_trusted_but_failed_receipt_is_not_an_analysis_input(self) -> None:
        records, _trusted = equal_success_bundle()
        receipt = one(records, "validation_receipt_v1")
        receipt["passed"] = False
        receipt["retention_decision"] = "reject"
        analysis = one(records, "analysis_summary_v1")
        analysis["input_validation_receipt_sha256s"][0] = sha256_json(receipt)
        trusted = context(
            records,
            trusted_receipts=set(analysis["input_validation_receipt_sha256s"]),
        )
        codes = {
            issue.code for issue in validate_cross_record_bundle(records, trusted)
        }
        self.assertIn("cross.analysis.receipt_validation", codes)

    def test_missing_or_duplicate_success_target_comparison_is_rejected(self) -> None:
        records, trusted = equal_success_bundle()
        analysis = one(records, "analysis_summary_v1")
        analysis["comparisons"][1] = deepcopy(analysis["comparisons"][0])
        codes = {
            issue.code for issue in validate_cross_record_bundle(records, trusted)
        }
        self.assertIn("cross.analysis.success_targets", codes)

    def test_wrong_log2_and_seed_binding_are_rejected(self) -> None:
        records, trusted = equal_success_bundle()
        comparison = one(records, "analysis_summary_v1")["comparisons"][0]
        comparison["log2_subgroup_order_decimal"] = "12.508537595346"
        comparison["independent_seed_count"] = 3
        comparison["algorithm_seed_set_sha256"] = "f" * 64
        codes = {
            issue.code for issue in validate_cross_record_bundle(records, trusted)
        }
        self.assertIn("cross.analysis.order_binding", codes)
        self.assertIn("cross.analysis.seed_binding", codes)

    def test_wrong_residual_observation_and_extra_model_fit_are_rejected(self) -> None:
        records, trusted = equal_success_bundle()
        analysis = one(records, "analysis_summary_v1")
        analysis["model_fits"][0]["residuals"][0]["curve_fixture_id"] = "foreign"
        analysis["model_fits"].append(deepcopy(analysis["model_fits"][0]))
        codes = {
            issue.code for issue in validate_cross_record_bundle(records, trusted)
        }
        self.assertIn("cross.analysis.model_binding", codes)

    def test_reversed_clustered_uncertainty_bounds_are_rejected(self) -> None:
        records, trusted = equal_success_bundle()
        uncertainty = one(records, "analysis_summary_v1")["comparisons"][0][
            "clustered_uncertainty"
        ]
        uncertainty["lower_decimal"] = "2"
        uncertainty["upper_decimal"] = "1"
        codes = {
            issue.code for issue in validate_cross_record_bundle(records, trusted)
        }
        self.assertIn("cross.analysis.uncertainty_binding", codes)


if __name__ == "__main__":
    unittest.main()
