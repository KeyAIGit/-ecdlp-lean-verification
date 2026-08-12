from __future__ import annotations

from copy import deepcopy
import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.ecdlp_lab.core.canonical import sha256_json
from experiments.ecdlp_lab.core.catalog_registry import trusted_catalog_sha256s
from experiments.ecdlp_lab.core.contracts import (
    ValidationContext,
    derive_campaign_id,
    validate_contract,
    validate_cross_record_bundle,
)
from experiments.ecdlp_lab.core.target_registry import (
    load_target_pair,
    load_target_pairs,
    load_target_registry,
)
from experiments.ecdlp_lab.orchestration.model import OrchestrationError
from experiments.ecdlp_lab.orchestration.provenance import (
    P04_BASE_SOURCE_COMMIT,
    build_campaign_provenance,
)
from experiments.ecdlp_lab.orchestration.records import (
    expand_campaign,
    load_smoke_campaign,
)


REPO_ROOT = Path(__file__).resolve().parents[3]


class P04ExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.pair = load_target_pair(repo_root=REPO_ROOT)
        cls.campaign = load_smoke_campaign(repo_root=REPO_ROOT)
        cls.campaign["provenance"] = build_campaign_provenance(
            config_sha256=cls.campaign["campaign_id"],
            source_commit=P04_BASE_SOURCE_COMMIT,
            source_tree_clean=False,
            diff_sha256=None,
            method_ids=cls.campaign["matrix"]["method_ids"],
            repo_root=REPO_ROOT,
        )

    def _multi_campaign(self, count: int = 2):
        authorities = load_target_registry(repo_root=REPO_ROOT)[:count]
        pairs = load_target_pairs(
            sorted(row.public_target_vector_sha256 for row in authorities),
            repo_root=REPO_ROOT,
        )
        campaign = deepcopy(self.campaign)
        campaign["matrix"]["target_vector_sha256s"] = sorted(
            pair.public_target_vector_sha256 for pair in pairs
        )
        campaign["matrix"]["curve_catalog_sha256s"] = sorted(
            {pair.public_payload["curve_catalog_sha256"] for pair in pairs}
        )
        campaign["matrix"]["curve_fixture_ids"] = sorted(
            {pair.public_payload["curve_fixture_id"] for pair in pairs}
        )
        campaign["expected_work_unit_count"] = 2 * len(pairs)
        campaign["campaign_id"] = derive_campaign_id(campaign)
        campaign["provenance"] = build_campaign_provenance(
            config_sha256=campaign["campaign_id"],
            source_commit=P04_BASE_SOURCE_COMMIT,
            source_tree_clean=False,
            diff_sha256=None,
            method_ids=campaign["matrix"]["method_ids"],
            repo_root=REPO_ROOT,
        )
        return campaign, pairs

    def test_smoke_is_one_target_times_two_methods_times_seed_seven(self) -> None:
        first = expand_campaign(
            self.campaign, target_pair=self.pair, repo_root=REPO_ROOT
        )
        second = expand_campaign(
            self.campaign, target_pair=self.pair, repo_root=REPO_ROOT
        )
        self.assertEqual(first, second)
        self.assertEqual(len(first.work_units), 2)
        identities = [work["identity"] for work in first.work_units]
        self.assertEqual(
            {identity["method_id"] for identity in identities},
            {"bsgs_v1", "ordinary_rho_xmod3_v1"},
        )
        self.assertEqual({identity["algorithm_seed"] for identity in identities}, {7})
        self.assertEqual({identity["repetition_ordinal"] for identity in identities}, {0})
        self.assertEqual(
            {identity["public_target_vector_sha256"] for identity in identities},
            {self.pair.public_target_vector_sha256},
        )
        self.assertEqual(len({work["work_unit_id"] for work in first.work_units}), 2)
        self.assertEqual(
            len(first.campaign["provenance"]["producer_dependency_sha256s"]), 1
        )
        self.assertEqual(
            len(
                {
                    identity["method_implementation_sha256"]
                    for identity in identities
                }
            ),
            1,
        )
        for work in first.work_units:
            self.assertEqual(work["work_unit_id"], sha256_json(work["identity"]))
            self.assertEqual(
                work["identity"]["campaign_config_sha256"],
                sha256_json(first.campaign),
            )

    def test_campaign_and_expansion_remain_p01_schema_and_bundle_valid(self) -> None:
        plan = expand_campaign(
            self.campaign, target_pair=self.pair, repo_root=REPO_ROOT
        )
        context = ValidationContext.from_records(
            (self.pair.public_record, self.pair.private_record),
            repo_root=REPO_ROOT,
            known_catalog_sha256s=trusted_catalog_sha256s(repo_root=REPO_ROOT),
            known_target_vector_sha256s=(self.pair.public_target_vector_sha256,),
            verify_artifacts=False,
        )
        self.assertEqual(validate_contract(plan.campaign, context), [])
        for work in plan.work_units:
            self.assertEqual(validate_contract(work, context), [])
        self.assertEqual(
            validate_cross_record_bundle(
                [
                    plan.campaign,
                    self.pair.public_record,
                    self.pair.private_record,
                    *plan.work_units,
                ],
                context,
            ),
            [],
        )

    def test_multi_target_axis_expands_bound_tuples_not_cartesian_pairs(self) -> None:
        campaign, pairs = self._multi_campaign(3)
        plan = expand_campaign(
            campaign, target_pairs=pairs, repo_root=REPO_ROOT
        )
        self.assertEqual(len(plan.work_units), 6)
        expected = {
            (
                pair.public_target_vector_sha256,
                pair.public_payload["curve_catalog_sha256"],
                pair.public_payload["curve_fixture_id"],
                method,
            )
            for pair in pairs
            for method in campaign["matrix"]["method_ids"]
        }
        observed = {
            (
                work["identity"]["public_target_vector_sha256"],
                work["identity"]["curve_catalog_sha256"],
                work["identity"]["curve_fixture_id"],
                work["identity"]["method_id"],
            )
            for work in plan.work_units
        }
        self.assertEqual(observed, expected)

    def test_incomplete_or_extra_target_allowlists_fail_before_dependencies(self) -> None:
        base, pairs = self._multi_campaign(2)
        mutations = (
            ("target_vector_sha256s", lambda axis: axis.pop()),
            ("curve_catalog_sha256s", lambda axis: axis.append("e" * 64)),
            ("curve_fixture_ids", lambda axis: axis.append("second-fixture")),
        )
        for axis, mutation in mutations:
            with self.subTest(axis=axis):
                campaign = deepcopy(base)
                mutation(campaign["matrix"][axis])
                with patch(
                    "experiments.ecdlp_lab.orchestration.records.allowed_method_ids",
                    side_effect=AssertionError("dependencies must not resolve"),
                ):
                    with self.assertRaises(OrchestrationError):
                        expand_campaign(
                            campaign, target_pairs=pairs, repo_root=REPO_ROOT
                        )

    def test_unknown_method_and_configured_executable_text_are_rejected(self) -> None:
        campaign = deepcopy(self.campaign)
        campaign["matrix"]["method_ids"] = ["bsgs_v1", "shell_v1"]
        with self.assertRaises(OrchestrationError):
            expand_campaign(campaign, target_pair=self.pair, repo_root=REPO_ROOT)

        campaign = deepcopy(self.campaign)
        campaign["allowed_method_ids"] = ["bsgs_v1", "ordinary_rho_xmod3_v1;python"]
        with self.assertRaisesRegex(OrchestrationError, "allowlist.binding"):
            expand_campaign(campaign, target_pair=self.pair, repo_root=REPO_ROOT)

    def test_expansion_and_algorithm_budgets_have_container_safe_ceilings(self) -> None:
        campaign = deepcopy(self.campaign)
        campaign["matrix"]["algorithm_seeds"] = list(range(65))
        campaign["expected_work_unit_count"] = 130
        with self.assertRaisesRegex(OrchestrationError, "matrix.ceiling"):
            expand_campaign(campaign, target_pair=self.pair, repo_root=REPO_ROOT)

        campaign = deepcopy(self.campaign)
        campaign["budgets"]["max_steps"] = 100_001
        with self.assertRaisesRegex(OrchestrationError, "budgets.ceiling"):
            expand_campaign(campaign, target_pair=self.pair, repo_root=REPO_ROOT)

    def test_campaign_rejects_false_clean_wrong_base_and_unbound_diff(self) -> None:
        mutations = (
            (
                "source_tree_clean",
                lambda provenance: provenance.update({"source_tree_clean": True}),
            ),
            (
                "source_commit",
                lambda provenance: provenance.update({"source_commit": "0" * 40}),
            ),
            (
                "diff_sha256",
                lambda provenance: provenance.update({"diff_sha256": None}),
            ),
            (
                "diff_sha256",
                lambda provenance: provenance.update({"diff_sha256": "f" * 64}),
            ),
        )
        self.assertEqual(
            self.campaign["provenance"]["source_commit"], P04_BASE_SOURCE_COMMIT
        )
        for expected_path, mutation in mutations:
            with self.subTest(expected_path=expected_path):
                campaign = deepcopy(self.campaign)
                mutation(campaign["provenance"])
                with self.assertRaisesRegex(OrchestrationError, expected_path):
                    expand_campaign(
                        campaign, target_pair=self.pair, repo_root=REPO_ROOT
                    )


if __name__ == "__main__":
    unittest.main()
