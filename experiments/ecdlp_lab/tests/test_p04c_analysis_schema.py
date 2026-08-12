from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest

from experiments.ecdlp_lab.core.canonical import load_json, sha256_json
from experiments.ecdlp_lab.core.schema import schema_definition_issues, validate_schema


LAB_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = LAB_ROOT / "contracts" / "analysis_summary_v1.schema.json"
FIXTURE_PATH = LAB_ROOT / "fixtures" / "contracts" / "valid" / "analysis_summary_v1.json"
TARGET_ID = "f530af54bbc7c68523bef1abcf97853d7c635244c15f5c071f91857ecf8083d8"
SEED_SET_ID = sha256_json([7, 11])


def _uncertainty() -> dict[str, object]:
    return {
        "method": "delete_one_cluster_envelope_v1",
        "cluster_count": 2,
        "lower_decimal": "90",
        "upper_decimal": "112",
    }


def _comparison(base: dict[str, object], target: str) -> dict[str, object]:
    comparison = deepcopy(base["comparisons"][0])
    comparison.update(
        {
            "public_target_vector_sha256": TARGET_ID,
            "curve_fixture_id": "toy-secp-j0-b13-c0-p5923",
            "subgroup_order": 5827,
            "log2_subgroup_order_decimal": "12.508537595347",
            "success_target_decimal": target,
            "independent_seed_count": 2,
            "algorithm_seed_set_sha256": SEED_SET_ID,
            "clustered_uncertainty": _uncertainty(),
        }
    )
    if target == "0.50":
        comparison.update(
            {
                "equal_success_status": "reached",
                "equal_success_attempts": 2,
                "expected_attempts_decimal": "2",
                "conservative_normalized_group_operations_decimal": "202",
                "optimistic_normalized_group_operations_decimal": "190",
                "equal_success_full_cost": deepcopy(comparison["full_cost"]),
            }
        )
    else:
        comparison.update(
            {
                "equal_success_status": "unreachable_within_budget",
                "equal_success_attempts": None,
                "expected_attempts_decimal": None,
                "conservative_normalized_group_operations_decimal": None,
                "optimistic_normalized_group_operations_decimal": None,
                "equal_success_full_cost": None,
            }
        )
    return comparison


def _fit(target: str) -> dict[str, object]:
    return {
        "method_id": "bsgs_v1",
        "success_target_decimal": target,
        "model_id": "model_undecided_v1",
        "status": "insufficient_data",
        "coefficients": [],
        "warning_codes": ["too_few_sizes"],
        "clustered_uncertainty": _uncertainty(),
        "residuals": [
            {
                "curve_fixture_id": "toy-secp-j0-b13-c0-p5923",
                "subgroup_order": 5827,
                "observed_log2_cost_decimal": "7.658",
                "predicted_log2_cost_decimal": "7.658",
                "residual_decimal": "0",
            }
        ],
        "leave_one_size_out": [
            {
                "omitted_subgroup_order": 5827,
                "status": "insufficient_data",
                "alpha_decimal": None,
                "beta_decimal": None,
            }
        ],
    }


def equal_success_summary() -> dict[str, object]:
    summary = deepcopy(load_json(FIXTURE_PATH))
    summary.update(
        {
            "analysis_protocol_id": "equal_success_scaling_v1",
            "analysis_policies": {
                "success_estimation": "conservative_empirical_v1",
                "censoring": "exclude_primary_fit_report_sensitivity_v1",
                "unreachable": "null_cost_with_budget_bound_v1",
                "uncertainty": "delete_one_cluster_envelope_v1",
                "clustering": "curve_and_algorithm_seed_v1",
                "residuals": "log2_cost_v1",
                "outliers": "report_no_silent_drop_v1",
                "cross_validation": "leave_one_distinct_size_out_v1",
            },
            "comparisons": [
                _comparison(summary, "0.50"),
                _comparison(summary, "0.95"),
            ],
            "model_fits": [_fit("0.50"), _fit("0.95")],
        }
    )
    return summary


class P04CAnalysisSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = load_json(SCHEMA_PATH)
        cls.legacy = load_json(FIXTURE_PATH)

    def test_schema_is_supported_and_legacy_p01_summary_remains_valid(self) -> None:
        self.assertEqual(schema_definition_issues(self.schema), [])
        self.assertNotIn("analysis_protocol_id", self.legacy)
        self.assertEqual(validate_schema(self.legacy, self.schema), [])

    def test_equal_success_protocol_accepts_reached_and_unreachable_targets(self) -> None:
        summary = equal_success_summary()
        self.assertEqual(validate_schema(summary, self.schema), [])
        self.assertEqual(
            [row["success_target_decimal"] for row in summary["comparisons"]],
            ["0.50", "0.95"],
        )
        unreachable = summary["comparisons"][1]
        self.assertEqual(unreachable["equal_success_status"], "unreachable_within_budget")
        self.assertIsNone(unreachable["equal_success_full_cost"])

    def test_protocol_requires_exact_policies_and_050_095_targets(self) -> None:
        summary = equal_success_summary()
        del summary["analysis_policies"]
        self.assertNotEqual(validate_schema(summary, self.schema), [])

        wrong_policy = equal_success_summary()
        wrong_policy["analysis_policies"]["outliers"] = "silently_drop_v1"
        self.assertNotEqual(validate_schema(wrong_policy, self.schema), [])

        collapsed_targets = equal_success_summary()
        collapsed_targets["success_targets_decimal"] = ["0.50", "0.50"]
        self.assertNotEqual(validate_schema(collapsed_targets, self.schema), [])

    def test_reached_and_unreachable_nullability_is_fail_closed(self) -> None:
        reached_without_cost = equal_success_summary()
        reached_without_cost["comparisons"][0]["equal_success_full_cost"] = None
        self.assertNotEqual(validate_schema(reached_without_cost, self.schema), [])

        unreachable_with_cost = equal_success_summary()
        unreachable_with_cost["comparisons"][1][
            "conservative_normalized_group_operations_decimal"
        ] = "999"
        self.assertNotEqual(validate_schema(unreachable_with_cost, self.schema), [])

    def test_uncertainty_residual_and_leave_one_size_out_are_mandatory(self) -> None:
        mutations = (
            ("comparisons", 0, "clustered_uncertainty"),
            ("model_fits", 0, "clustered_uncertainty"),
            ("model_fits", 0, "residuals"),
            ("model_fits", 0, "leave_one_size_out"),
        )
        for collection, index, field in mutations:
            with self.subTest(field=field):
                summary = equal_success_summary()
                del summary[collection][index][field]
                self.assertNotEqual(validate_schema(summary, self.schema), [])

    def test_nonfitted_leave_one_size_out_cannot_claim_coefficients(self) -> None:
        summary = equal_success_summary()
        summary["model_fits"][0]["leave_one_size_out"][0]["alpha_decimal"] = "0.5"
        self.assertNotEqual(validate_schema(summary, self.schema), [])

    def test_protocol_fields_are_forbidden_without_protocol_id(self) -> None:
        summary = equal_success_summary()
        del summary["analysis_protocol_id"]
        self.assertNotEqual(validate_schema(summary, self.schema), [])


if __name__ == "__main__":
    unittest.main()
