from __future__ import annotations

import unittest
from copy import deepcopy
from pathlib import Path

from experiments.ecdlp_lab.core.canonical import load_json, sha256_json
from experiments.ecdlp_lab.core.contracts import (
    ValidationContext,
    derive_campaign_id,
    derive_target_vector_id,
    validate_contract,
    validate_cross_record_bundle,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
VALID_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "contracts" / "valid"


def fixture(name: str) -> dict[str, object]:
    value = load_json(VALID_ROOT / name)
    assert isinstance(value, dict)
    return value


def refresh_campaign(campaign: dict[str, object]) -> None:
    campaign["campaign_id"] = derive_campaign_id(campaign)
    campaign["provenance"]["config_sha256"] = campaign["campaign_id"]


class TargetDrivenCampaignTests(unittest.TestCase):
    def setUp(self) -> None:
        self.campaign = fixture("campaign_config_v1.json")
        self.public = fixture("target_vector_public_v1.json")
        self.work = fixture("work_unit_v1.json")

    def second_target(self) -> dict[str, object]:
        second = deepcopy(self.public)
        payload = second["public_payload"]
        payload["curve_catalog_sha256"] = "a" * 64
        payload["curve_fixture_id"] = "second-target-fixture"
        payload["curve_id"] = "second-target-fixture"
        second["target_vector_id"] = derive_target_vector_id(second)
        return second

    def context(self, *targets: dict[str, object]) -> ValidationContext:
        return ValidationContext.from_records(
            targets,
            known_catalog_sha256s={
                target["public_payload"]["curve_catalog_sha256"] for target in targets
            },
            known_target_vector_sha256s={
                target["target_vector_id"] for target in targets
            },
            verify_artifacts=False,
        )

    def test_count_uses_targets_as_leading_axis_not_catalog_cartesian_product(self) -> None:
        second = self.second_target()
        matrix = self.campaign["matrix"]
        matrix["target_vector_sha256s"].append(second["target_vector_id"])
        matrix["curve_catalog_sha256s"].append(
            second["public_payload"]["curve_catalog_sha256"]
        )
        matrix["curve_fixture_ids"].append(
            second["public_payload"]["curve_fixture_id"]
        )
        self.campaign["expected_work_unit_count"] = 2
        refresh_campaign(self.campaign)
        self.assertEqual(
            validate_contract(self.campaign, self.context(self.public, second)), []
        )

    def test_catalog_and_fixture_axes_are_exact_authenticated_target_sets(self) -> None:
        second = self.second_target()
        matrix = self.campaign["matrix"]
        matrix["target_vector_sha256s"].append(second["target_vector_id"])
        matrix["curve_catalog_sha256s"] = [
            self.public["public_payload"]["curve_catalog_sha256"]
        ]
        matrix["curve_fixture_ids"].append("unauthorized-fixture")
        self.campaign["expected_work_unit_count"] = 2
        refresh_campaign(self.campaign)
        codes = {
            issue.code
            for issue in validate_contract(
                self.campaign, self.context(self.public, second)
            )
        }
        self.assertIn("contract.campaign.catalog_allowlist", codes)
        self.assertIn("contract.campaign.fixture_allowlist", codes)

    def test_bundle_rejects_cross_target_catalog_fixture_pair(self) -> None:
        second = self.second_target()
        matrix = self.campaign["matrix"]
        matrix["target_vector_sha256s"].append(second["target_vector_id"])
        matrix["curve_catalog_sha256s"].append(
            second["public_payload"]["curve_catalog_sha256"]
        )
        matrix["curve_fixture_ids"].append(
            second["public_payload"]["curve_fixture_id"]
        )
        matrix["method_ids"] = [self.work["identity"]["method_id"]]
        self.campaign["allowed_method_ids"] = matrix["method_ids"]
        self.campaign["expected_work_unit_count"] = 2
        refresh_campaign(self.campaign)

        first_work = deepcopy(self.work)
        first_work["campaign_id"] = self.campaign["campaign_id"]
        first_work["identity"]["campaign_config_sha256"] = sha256_json(self.campaign)
        first_work["work_unit_id"] = sha256_json(first_work["identity"])
        first_work["attempt_id"] = sha256_json(
            {"retry_ordinal": 0, "work_unit_id": first_work["work_unit_id"]}
        )
        crossed = deepcopy(first_work)
        crossed["identity"]["public_target_vector_sha256"] = second[
            "target_vector_id"
        ]
        # Deliberately retain the first target's catalog/fixture.
        crossed["work_unit_id"] = sha256_json(crossed["identity"])
        crossed["attempt_id"] = sha256_json(
            {"retry_ordinal": 0, "work_unit_id": crossed["work_unit_id"]}
        )
        codes = {
            issue.code
            for issue in validate_cross_record_bundle(
                [self.campaign, self.public, second, first_work, crossed],
                self.context(self.public, second),
            )
        }
        self.assertIn("cross.work.target_binding", codes)
        self.assertIn("cross.campaign.coverage", codes)


if __name__ == "__main__":
    unittest.main()
