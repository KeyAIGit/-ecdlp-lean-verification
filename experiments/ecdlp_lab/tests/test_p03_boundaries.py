from __future__ import annotations

import unittest
from dataclasses import asdict, fields

from experiments.ecdlp_lab.core.candidate_validation import validate_candidate
from experiments.ecdlp_lab.core.catalog_registry import (
    CI_CATALOG_ID,
    LEGACY_CATALOG_ID,
    CatalogRegistryError,
    load_catalog_registry,
    resolve_curve_fixture,
)
from experiments.ecdlp_lab.methods.python.model import MethodBudgets, PublicMethodInput
from experiments.framework.ec_oracle import Curve as OracleCurve


class P03BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.authorities = {
            authority.catalog_id: authority for authority in load_catalog_registry()
        }

    def test_registry_resolves_ci_and_legacy_public_fixtures(self) -> None:
        ci = resolve_curve_fixture(
            self.authorities[CI_CATALOG_ID].sha256,
            "ecdlp-lab-j0-glv-like-b11-p1051-g0",
        )
        self.assertEqual(ci.catalog_sha256, self.authorities[CI_CATALOG_ID].sha256)
        self.assertEqual(ci.generator, (863, 955))
        self.assertEqual(ci.subgroup_order, 1093)

        legacy = resolve_curve_fixture(
            self.authorities[LEGACY_CATALOG_ID].sha256,
            "toy-secp-j0-b13-c0-p5923-g0",
        )
        self.assertEqual(
            legacy.catalog_sha256, self.authorities[LEGACY_CATALOG_ID].sha256
        )
        self.assertEqual(legacy.generator, (21, 4509))
        self.assertEqual(legacy.subgroup_order, 5827)

        legacy_base = resolve_curve_fixture(
            self.authorities[LEGACY_CATALOG_ID].sha256,
            "toy-secp-j0-b13-c0-p5923",
        )
        self.assertEqual(legacy_base.generator, (3665, 430))

    def test_registry_fixture_resolution_fails_closed(self) -> None:
        with self.assertRaises(CatalogRegistryError):
            resolve_curve_fixture("f" * 64, "any-fixture")
        with self.assertRaises(CatalogRegistryError):
            resolve_curve_fixture(
                self.authorities[CI_CATALOG_ID].sha256,
                "unknown-fixture",
            )
        with self.assertRaises(CatalogRegistryError):
            resolve_curve_fixture(self.authorities[CI_CATALOG_ID].sha256, "")

    def test_public_method_input_is_secret_free_and_oracle_compatible(self) -> None:
        fixture = resolve_curve_fixture(
            self.authorities[CI_CATALOG_ID].sha256,
            "ecdlp-lab-j0-glv-like-b11-p1051-g0",
        )
        candidate = 41
        oracle = OracleCurve(fixture.field_p, fixture.curve_a, fixture.curve_b)
        target = oracle.scalar_mul(candidate, fixture.generator)
        self.assertIsNotNone(target)
        budgets = MethodBudgets(
            max_subgroup_order_bits=32,
            max_field_bits=32,
            max_group_law_invocations=100_000,
            max_table_entries=65_536,
            max_steps=100_000,
            timeout_ns=5_000_000_000,
            max_memory_bytes=64 * 1024 * 1024,
            workers=1,
        )
        public_input = PublicMethodInput(
            method_id="bsgs_v1",
            algorithm_seed=7,
            p=fixture.field_p,
            a=fixture.curve_a,
            b=fixture.curve_b,
            G=fixture.generator,
            Q=target,
            ell=fixture.subgroup_order,
            budgets=budgets,
        )
        forbidden_fields = {
            "expected_scalar",
            "target_generation_scalar",
            "private_target_receipt",
            "source_record",
            "source_row",
            "legacy_row",
        }
        self.assertEqual(
            {field.name for field in fields(public_input)},
            {"method_id", "algorithm_seed", "p", "a", "b", "G", "Q", "ell", "budgets"},
        )
        self.assertTrue(forbidden_fields.isdisjoint(field.name for field in fields(public_input)))
        payload = asdict(public_input)
        self.assertTrue(forbidden_fields.isdisjoint(payload))
        self.assertNotIn("expected_scalar", repr(payload))
        self.assertTrue(validate_candidate(public_input, candidate).passed)


if __name__ == "__main__":
    unittest.main()
