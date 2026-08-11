from __future__ import annotations

import unittest
from copy import deepcopy
from pathlib import Path

from experiments.ecdlp_lab.core.canonical import (
    load_json,
    sha256_file,
    sha256_json,
)
from experiments.ecdlp_lab.core.contracts import (
    ValidationContext,
    validate_contract,
    validate_cross_record_bundle,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
RECEIPT_PATH = (
    REPO_ROOT
    / "experiments"
    / "ecdlp_lab"
    / "fixtures"
    / "contracts"
    / "valid"
    / "validation_receipt_v1.json"
)
ARTIFACT_PATH = RECEIPT_PATH.with_name("artifact_ref_v1.json")
CATALOG_PATH = (
    REPO_ROOT
    / "experiments"
    / "ecdlp_lab"
    / "fixtures"
    / "curves"
    / "ci_curve_catalog_v1.json"
)


def catalog_receipt() -> dict[str, object]:
    receipt = deepcopy(load_json(RECEIPT_PATH))
    receipt.update(
        {
            "subject_contract_kind": "artifact_ref_v1",
            "candidate_scalar": None,
            "candidate_relation_valid": None,
            "private_target_receipt_sha256": None,
        }
    )
    return receipt


class CatalogReceiptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.context = ValidationContext(repo_root=REPO_ROOT, verify_artifacts=False)

    def test_passed_artifact_receipt_uses_null_candidate_fields(self) -> None:
        self.assertEqual(validate_contract(catalog_receipt(), self.context), [])

    def test_catalog_artifact_and_receipt_form_a_coherent_mini_bundle(self) -> None:
        artifact = deepcopy(load_json(ARTIFACT_PATH))
        catalog_sha256 = sha256_file(CATALOG_PATH)
        artifact.update(
            {
                "artifact_id": catalog_sha256,
                "sha256": catalog_sha256,
                "size_bytes": CATALOG_PATH.stat().st_size,
                "location": (
                    "experiments/ecdlp_lab/fixtures/curves/"
                    "ci_curve_catalog_v1.json"
                ),
                "role": "curve_catalog",
                "producer_contract_kind": None,
            }
        )
        receipt = catalog_receipt()
        receipt.update(
            {
                "subject_id": artifact["artifact_id"],
                "subject_sha256": sha256_json(artifact),
            }
        )
        context = ValidationContext(repo_root=REPO_ROOT, verify_artifacts=True)
        self.assertEqual(
            validate_cross_record_bundle([artifact, receipt], context), []
        )

    def test_non_method_receipt_rejects_candidate_material(self) -> None:
        for field_name, value in (
            ("candidate_scalar", 1),
            ("candidate_relation_valid", True),
            ("private_target_receipt_sha256", "1" * 64),
        ):
            with self.subTest(field_name=field_name):
                receipt = catalog_receipt()
                receipt[field_name] = value
                issues = validate_contract(receipt, self.context)
                self.assertIn(
                    "contract.validation.non_method_candidate",
                    {issue.code for issue in issues},
                )

    def test_passed_method_result_still_requires_valid_relation(self) -> None:
        receipt = deepcopy(load_json(RECEIPT_PATH))
        receipt["candidate_relation_valid"] = None
        issues = validate_contract(receipt, self.context)
        self.assertIn(
            "contract.validation.relation", {issue.code for issue in issues}
        )


if __name__ == "__main__":
    unittest.main()
