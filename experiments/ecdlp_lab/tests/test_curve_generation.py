from __future__ import annotations

import ast
import unittest
from copy import deepcopy
from pathlib import Path

from experiments.ecdlp_lab.core.canonical import load_json, sha256_bytes
from experiments.ecdlp_lab.core.schema import schema_definition_issues, validate_schema
from experiments.ecdlp_lab.curves.generate_ci_catalog import (
    CI_CATALOG_PATH,
    CatalogSpecError,
    SearchExhausted,
    SearchState,
    check_committed_catalog,
    committed_catalog_bytes,
    generate_catalog,
    load_spec,
    main,
    render_catalog,
)
from experiments.ecdlp_lab.curves.model import ResolvedCurveFixture


LAB_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = LAB_ROOT / "curves/catalog_schema.json"
PRODUCER_ADAPTER_PATH = LAB_ROOT / "curves/producer_adapter.py"


class CurveGenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = load_spec()
        cls.catalog = generate_catalog(cls.spec)
        cls.rendered = render_catalog(cls.catalog)

    def test_generation_is_byte_identical_to_committed_catalog(self) -> None:
        second = render_catalog(generate_catalog(deepcopy(self.spec)))
        self.assertEqual(self.rendered, second)
        self.assertEqual(self.rendered, committed_catalog_bytes())
        self.assertEqual(
            sha256_bytes(self.rendered),
            "7f125738007c5399a545ae4d0309335f0362d6feb5431c05e3d17665cdf03a0a",
        )
        self.assertEqual(
            check_committed_catalog(),
            (
                True,
                "7f125738007c5399a545ae4d0309335f0362d6feb5431c05e3d17665cdf03a0a",
            ),
        )

    def test_exact_six_prototypes_and_global_counter_receipts(self) -> None:
        observed = {
            (entry["family"], entry["field_bits"]): (
                entry["field_p"],
                entry["curve_a"],
                entry["curve_b"],
                entry["full_order"],
                entry["subgroup_order"],
                entry["cofactor"],
                entry["generator"],
                entry["generation_search"],
            )
            for entry in self.catalog["fixtures"]
        }
        expected = {
            ("j0_glv_like", 11): (
                1051,
                0,
                7,
                1093,
                1093,
                1,
                [863, 955],
                {
                    "prime_candidates_examined": 45,
                    "curve_candidates_examined": 9,
                    "point_attempts": 22,
                },
            ),
            ("random_generic_j_prime_subgroup", 11): (
                1069,
                710,
                553,
                1124,
                281,
                4,
                [207, 709],
                {
                    "prime_candidates_examined": 3,
                    "curve_candidates_examined": 8,
                    "point_attempts": 1,
                },
            ),
            ("j0_no_fp_glv_control", 11): (
                1613,
                0,
                7,
                1614,
                269,
                6,
                [364, 1048],
                {
                    "prime_candidates_examined": 221,
                    "curve_candidates_examined": 34,
                    "point_attempts": 2,
                },
            ),
            ("j0_glv_like", 13): (
                6709,
                0,
                7,
                6829,
                6829,
                1,
                [2336, 6475],
                {
                    "prime_candidates_examined": 3,
                    "curve_candidates_examined": 1,
                    "point_attempts": 1,
                },
            ),
            ("random_generic_j_prime_subgroup", 13): (
                7753,
                77,
                1022,
                7841,
                7841,
                1,
                [7732, 5106],
                {
                    "prime_candidates_examined": 5,
                    "curve_candidates_examined": 8,
                    "point_attempts": 1,
                },
            ),
            ("j0_no_fp_glv_control", 13): (
                6197,
                0,
                7,
                6198,
                1033,
                6,
                [3891, 1594],
                {
                    "prime_candidates_examined": 721,
                    "curve_candidates_examined": 84,
                    "point_attempts": 2,
                },
            ),
        }
        self.assertEqual(observed, expected)
        self.assertEqual(
            list(observed),
            [
                ("j0_glv_like", 11),
                ("random_generic_j_prime_subgroup", 11),
                ("j0_no_fp_glv_control", 11),
                ("j0_glv_like", 13),
                ("random_generic_j_prime_subgroup", 13),
                ("j0_no_fp_glv_control", 13),
            ],
        )

    def test_catalog_schema_is_supported_and_accepts_catalog(self) -> None:
        schema = load_json(SCHEMA_PATH)
        self.assertIsInstance(schema, dict)
        self.assertEqual(schema_definition_issues(schema), [])
        self.assertEqual(validate_schema(self.catalog, schema), [])

    def test_catalog_contains_no_observational_provenance(self) -> None:
        forbidden = {
            "wall_time_seconds",
            "timing",
            "platform",
            "python",
            "source_commit",
            "source_worktree_dirty",
            "dirty",
        }

        def walk(value: object) -> None:
            if isinstance(value, dict):
                self.assertTrue(forbidden.isdisjoint(value))
                for child in value.values():
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)
            else:
                self.assertNotIsInstance(value, float)

        walk(self.catalog)

    def test_every_entry_projects_to_the_immutable_consumer_model(self) -> None:
        digest = sha256_bytes(self.rendered)
        for entry in self.catalog["fixtures"]:
            with self.subTest(fixture=entry["fixture_id"]):
                fixture = ResolvedCurveFixture.from_catalog_entry(
                    entry, catalog_sha256=digest
                )
                self.assertEqual(fixture.field_bits, fixture.field_p.bit_length())
                self.assertEqual(
                    fixture.subgroup_order_bits, fixture.subgroup_order.bit_length()
                )
                self.assertEqual(
                    fixture.full_order, fixture.cofactor * fixture.subgroup_order
                )

    def test_counters_are_global_and_fail_at_the_frozen_ceiling(self) -> None:
        state = SearchState(
            "j0_glv_like",
            11,
            {
                "max_prime_candidates": 1,
                "max_curve_candidates": 1,
                "max_point_attempts": 1,
            },
        )
        self.assertEqual(state.consume("point_attempts"), 0)
        with self.assertRaisesRegex(SearchExhausted, "max_point_attempts"):
            state.consume("point_attempts")
        self.assertEqual(state.point_attempts, 1)

    def test_spec_policy_and_parameter_drift_is_rejected_in_memory(self) -> None:
        raised = deepcopy(self.spec)
        raised["limits"]["max_point_attempts"] = 1025
        with self.assertRaises(CatalogSpecError):
            generate_catalog(raised)
        renamed = deepcopy(self.spec)
        renamed["catalog_nonce"] = "unreviewed"
        with self.assertRaises(CatalogSpecError):
            generate_catalog(renamed)
        policy_drift = deepcopy(self.spec)
        policy_drift["search_policy"]["generic_curves_per_prime"] = 65
        with self.assertRaisesRegex(CatalogSpecError, "search policy drifted"):
            generate_catalog(policy_drift)
        parameter_drift = deepcopy(self.spec)
        parameter_drift["family_parameters"]["j0_glv_like"]["curve_a"] = False
        with self.assertRaisesRegex(CatalogSpecError, "family parameters drifted"):
            generate_catalog(parameter_drift)

    def test_adapter_does_not_import_unbounded_legacy_searches(self) -> None:
        tree = ast.parse(PRODUCER_ADAPTER_PATH.read_text(encoding="utf-8"))
        imported = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
        }
        self.assertNotIn("search_curve", imported)
        self.assertNotIn("deterministic_point", imported)

    def test_check_cli_passes_without_writing(self) -> None:
        before = CI_CATALOG_PATH.read_bytes()
        self.assertEqual(main(["--check"]), 0)
        self.assertEqual(CI_CATALOG_PATH.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
