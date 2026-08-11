from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.ecdlp_lab.core.canonical import load_json, sha256_file
from experiments.ecdlp_lab.curves.p1_adapter import (
    LEGACY_CATALOG_PATH,
    LEGACY_CATALOG_SHA256,
    LegacyCatalogError,
    _safe_legacy_json,
    load_legacy_catalog,
    resolve_legacy_base_point,
    resolve_legacy_generator,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = (
    REPO_ROOT / "experiments/ecdlp_lab/fixtures/curves/catalog_registry_v1.json"
)


class P1CatalogAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        registry = load_json(REGISTRY_PATH)
        if not isinstance(registry, dict) or not isinstance(registry.get("catalogs"), list):
            raise AssertionError("invalid test catalog registry")
        cls.authority = next(
            row
            for row in registry["catalogs"]
            if row.get("catalog_id") == "legacy_p1_curve_catalog"
        )
        cls.catalog = load_legacy_catalog(
            catalog_path=cls.authority["path"],
            catalog_sha256=cls.authority["sha256"],
        )

    def test_registry_authority_loads_exactly_40_sorted_curves(self) -> None:
        self.assertEqual(self.catalog.raw_sha256, LEGACY_CATALOG_SHA256)
        self.assertEqual(len(self.catalog.curves), 40)
        self.assertEqual(
            [(curve.field_bits, curve.curve_index) for curve in self.catalog.curves],
            sorted(
                (curve.field_bits, curve.curve_index) for curve in self.catalog.curves
            ),
        )
        self.assertEqual(
            {curve.field_bits for curve in self.catalog.curves}, {13, 16, 20, 24}
        )
        self.assertTrue(all(len(curve.generators) == 6 for curve in self.catalog.curves))

    def test_recorded_generator_locator_projects_without_observations(self) -> None:
        fixture = resolve_legacy_generator(13, 0, 0, catalog=self.catalog)
        self.assertEqual(fixture.curve_id, "toy-secp-j0-b13-c0-p5923")
        self.assertEqual(fixture.fixture_id, "toy-secp-j0-b13-c0-p5923-g0")
        self.assertEqual(fixture.generator, (21, 4509))
        self.assertEqual(fixture.subgroup_order, 5827)
        self.assertEqual(fixture.beta, 428)
        self.assertEqual(fixture.lambda_value, 1350)
        self.assertEqual(fixture.source_kind, "read_only_legacy_catalog")

    def test_base_point_compatibility_locator_is_explicit(self) -> None:
        fixture = resolve_legacy_base_point(
            "toy-secp-j0-b13-c0-p5923", catalog=self.catalog
        )
        self.assertEqual(fixture.fixture_id, fixture.curve_id)
        self.assertEqual(fixture.generator, (3665, 430))

    def test_wrong_registry_digest_fails_before_legacy_parse(self) -> None:
        with patch(
            "experiments.ecdlp_lab.curves.p1_adapter._safe_legacy_json"
        ) as parser:
            with self.assertRaisesRegex(LegacyCatalogError, "digest mismatch"):
                load_legacy_catalog(
                    catalog_path=LEGACY_CATALOG_PATH,
                    catalog_sha256="0" * 64,
                )
            parser.assert_not_called()

    def test_legacy_parser_rejects_duplicates_and_nonfinite_numbers(self) -> None:
        with self.assertRaisesRegex(LegacyCatalogError, "duplicate"):
            _safe_legacy_json(b'{"a":1,"a":2}')
        with self.assertRaisesRegex(LegacyCatalogError, "non-finite"):
            _safe_legacy_json(b'{"value":NaN}')

    def test_legacy_artifact_is_byte_for_byte_unchanged(self) -> None:
        self.assertEqual(
            sha256_file(REPO_ROOT / LEGACY_CATALOG_PATH), LEGACY_CATALOG_SHA256
        )

    def test_unknown_generator_fails_closed(self) -> None:
        with self.assertRaises(KeyError):
            resolve_legacy_generator(13, 0, 99, catalog=self.catalog)


if __name__ == "__main__":
    unittest.main()
