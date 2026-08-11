from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.ecdlp_lab.core.canonical import load_json, sha256_file
from experiments.ecdlp_lab.curves.p1_adapter import (
    LEGACY_CATALOG_PATH,
    LEGACY_CATALOG_SHA256,
    load_legacy_catalog,
)
from experiments.ecdlp_lab.curves.validate_catalog import (
    FAMILIES,
    validate_catalog_bytes,
    validate_fixture,
    validate_legacy_catalog,
    validate_legacy_catalog_bytes,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
CURVE_FIXTURES = REPO_ROOT / "experiments/ecdlp_lab/fixtures/curves"
CI_SPEC = CURVE_FIXTURES / "ci_catalog_spec_v1.json"
CI_CATALOG = CURVE_FIXTURES / "ci_curve_catalog_v1.json"
LEGACY_CATALOG = REPO_ROOT / LEGACY_CATALOG_PATH


class IndependentCurveValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec_sha256 = sha256_file(CI_SPEC)
        cls.catalog = load_json(CI_CATALOG)
        if not isinstance(cls.catalog, dict):
            raise AssertionError("CI catalog is not an object")

    def test_committed_ci_catalog_passes_all_six_independent_checks(self) -> None:
        result = validate_catalog_bytes(
            CI_CATALOG.read_bytes(),
            expected_spec_sha256=self.spec_sha256,
            exact_count_authorized=True,
        )
        self.assertTrue(result.passed, result.issues)
        self.assertEqual(result.fixture_count, 6)
        self.assertEqual(result.declared_fixture_count, 6)
        self.assertEqual(result.catalog_sha256, sha256_file(CI_CATALOG))
        self.assertEqual(
            [(row.family, row.passed) for row in result.fixture_results],
            [(family, True) for _bits in (11, 13) for family in FAMILIES],
        )
        self.assertEqual(result.issues, ())

    def test_exact_certificates_fail_closed_without_trusted_spec_authority(self) -> None:
        result = validate_catalog_bytes(CI_CATALOG.read_bytes())
        codes = {issue.code for issue in result.issues}
        self.assertFalse(result.passed)
        self.assertIn("curve.catalog.spec_authority", codes)
        self.assertIn("curve.certificate.exact_unauthorized", codes)

    def test_false_or_non_boolean_exact_authority_cannot_enable_counting(self) -> None:
        generic = self.catalog["fixtures"][1]
        false_result = validate_fixture(generic, exact_count_authorized=False)
        string_result = validate_fixture(generic, exact_count_authorized="yes")
        self.assertIn(
            "curve.certificate.exact_unauthorized",
            {issue.code for issue in false_result.issues},
        )
        self.assertIn(
            "curve.certificate.exact_authority",
            {issue.code for issue in string_result.issues},
        )
        self.assertIn(
            "curve.certificate.exact_unauthorized",
            {issue.code for issue in string_result.issues},
        )

    def test_field_and_subgroup_widths_remain_distinct(self) -> None:
        generic_11 = self.catalog["fixtures"][1]
        self.assertEqual(generic_11["field_bits"], 11)
        self.assertEqual(generic_11["subgroup_order_bits"], 9)
        self.assertEqual(
            generic_11["field_p"].bit_length(), generic_11["field_bits"]
        )
        self.assertEqual(
            generic_11["subgroup_order"].bit_length(),
            generic_11["subgroup_order_bits"],
        )

    def test_report_is_deterministic_and_contains_no_observational_fields(self) -> None:
        first = validate_catalog_bytes(
            CI_CATALOG.read_bytes(), expected_spec_sha256=self.spec_sha256
        ).to_dict()
        second = validate_catalog_bytes(
            CI_CATALOG.read_bytes(), expected_spec_sha256=self.spec_sha256
        ).to_dict()
        self.assertEqual(first, second)
        encoded = json.dumps(first, sort_keys=True)
        for forbidden in (
            "wall_time",
            "platform",
            "source_commit",
            "dirty_tree",
        ):
            self.assertNotIn(forbidden, encoded)

    def test_legacy_bytes_validate_all_40_without_exact_counting(self) -> None:
        with patch(
            "experiments.ecdlp_lab.curves.validate_catalog._exact_legendre_full_order",
            side_effect=AssertionError("legacy validation attempted exact counting"),
        ):
            result = validate_legacy_catalog_bytes(
                LEGACY_CATALOG.read_bytes(),
                expected_catalog_sha256=LEGACY_CATALOG_SHA256,
            )
        self.assertTrue(result.passed, result.issues)
        self.assertEqual(result.fixture_count, 40)
        self.assertEqual(result.catalog_sha256, LEGACY_CATALOG_SHA256)
        self.assertEqual(
            {row.certificate_type for row in result.fixture_results},
            {"prime_order_hasse_unique_v1"},
        )

    def test_authenticated_legacy_adapter_object_uses_same_oracle_validation(self) -> None:
        catalog = load_legacy_catalog(
            catalog_path=LEGACY_CATALOG_PATH,
            catalog_sha256=LEGACY_CATALOG_SHA256,
            repo_root=REPO_ROOT,
        )
        result = validate_legacy_catalog(
            catalog, expected_catalog_sha256=LEGACY_CATALOG_SHA256
        )
        self.assertTrue(result.passed, result.issues)
        self.assertEqual(result.fixture_count, 40)


if __name__ == "__main__":
    unittest.main()
