from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable
from unittest.mock import patch

from experiments.ecdlp_lab.core.canonical import load_json, sha256_bytes, sha256_file
from experiments.ecdlp_lab.curves.p1_adapter import LEGACY_CATALOG_PATH
from experiments.ecdlp_lab.curves.validate_catalog import (
    validate_catalog_bytes,
    validate_fixture,
    validate_legacy_catalog_bytes,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
CURVE_FIXTURES = REPO_ROOT / "experiments/ecdlp_lab/fixtures/curves"
CI_SPEC = CURVE_FIXTURES / "ci_catalog_spec_v1.json"
CI_CATALOG = CURVE_FIXTURES / "ci_curve_catalog_v1.json"
LEGACY_CATALOG = REPO_ROOT / LEGACY_CATALOG_PATH


def render(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def assign(document: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    parent: Any = document
    for part in path[:-1]:
        parent = parent[part]
    parent[path[-1]] = value(parent[path[-1]]) if callable(value) else value


class CurveCertificateCorruptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_json(CI_CATALOG)
        if not isinstance(cls.catalog, dict):
            raise AssertionError("CI catalog is not an object")
        cls.spec_sha256 = sha256_file(CI_SPEC)

    def fixture_codes(
        self,
        index: int,
        path: tuple[str, ...],
        value: Any,
        *,
        exact_authorized: bool = True,
    ) -> set[str]:
        fixture = deepcopy(self.catalog["fixtures"][index])
        assign(fixture, path, value)
        return {
            issue.code
            for issue in validate_fixture(
                fixture, exact_count_authorized=exact_authorized
            ).issues
        }

    def test_universal_preflight_rejects_each_corrupted_primitive(self) -> None:
        cases = (
            ("boolean_p", 0, ("field_p",), True, "curve.field_prime"),
            ("oversize_p", 0, ("field_p",), 1 << 40, "curve.field_prime"),
            ("composite_p", 0, ("field_p",), 1053, "curve.field_prime"),
            ("wrong_field_bits", 0, ("field_bits",), 12, "curve.field_bits"),
            (
                "noncanonical_a",
                0,
                ("curve_a",),
                lambda _old: self.catalog["fixtures"][0]["field_p"],
                "curve.coefficient.canonical",
            ),
            ("singular_curve", 0, ("curve_b",), 0, "curve.nonsingular"),
            ("boolean_subgroup", 1, ("subgroup_order",), True, "curve.subgroup_prime"),
            ("composite_subgroup", 1, ("subgroup_order",), 9, "curve.subgroup_prime"),
            ("wrong_subgroup_bits", 1, ("subgroup_order_bits",), 10, "curve.subgroup_bits"),
            ("zero_cofactor", 1, ("cofactor",), 0, "curve.cofactor"),
            (
                "order_product",
                1,
                ("full_order",),
                lambda old: old + 1,
                "curve.order.product",
            ),
            ("generator_null", 0, ("generator",), None, "curve.generator.shape"),
            ("generator_bool", 0, ("generator",), [True, 1], "curve.generator.shape"),
            (
                "generator_noncanonical",
                0,
                ("generator",),
                [1051, 1],
                "curve.generator.canonical",
            ),
            ("generator_off_curve", 0, ("generator",), [0, 0], "curve.generator.off_curve"),
            ("wrong_j", 1, ("j_invariant",), 0, "curve.j_invariant"),
        )
        for name, index, path, value, expected in cases:
            with self.subTest(name=name):
                self.assertIn(expected, self.fixture_codes(index, path, value))

    def test_nonzero_on_curve_point_must_have_the_claimed_prime_order(self) -> None:
        fixture = deepcopy(self.catalog["fixtures"][1])
        fixture["subgroup_order"] = 2
        fixture["subgroup_order_bits"] = 2
        fixture["cofactor"] = 562
        codes = {
            issue.code
            for issue in validate_fixture(fixture, exact_count_authorized=True).issues
        }
        self.assertIn("curve.generator.order", codes)

    def test_each_certificate_branch_rejects_independent_corruption(self) -> None:
        unknown = self.fixture_codes(
            0, ("order_certificate", "type"), "made_up_certificate_v1"
        )
        self.assertIn("curve.certificate.unknown", unknown)

        bad_inputs = self.fixture_codes(
            0,
            ("order_certificate", "inputs", "hasse_upper"),
            lambda old: old + 1,
        )
        self.assertIn("curve.certificate.inputs", bad_inputs)

        hasse = deepcopy(self.catalog["fixtures"][0])
        hasse["cofactor"] = 2
        hasse["full_order"] = 2 * hasse["subgroup_order"]
        hasse_codes = {
            issue.code
            for issue in validate_fixture(hasse, exact_count_authorized=True).issues
        }
        self.assertIn("curve.certificate.hasse_unique", hasse_codes)

        exact = deepcopy(self.catalog["fixtures"][1])
        exact["cofactor"] = 5
        exact["full_order"] = 5 * exact["subgroup_order"]
        exact_codes = {
            issue.code
            for issue in validate_fixture(exact, exact_count_authorized=True).issues
        }
        self.assertIn("curve.certificate.exact_count", exact_codes)

        unauthorized = validate_fixture(
            self.catalog["fixtures"][1], exact_count_authorized=False
        )
        self.assertIn(
            "curve.certificate.exact_unauthorized",
            {issue.code for issue in unauthorized.issues},
        )

        oversize = deepcopy(self.catalog["fixtures"][1])
        oversize["field_p"] = 65537
        oversize["field_bits"] = 17
        oversize_codes = {
            issue.code
            for issue in validate_fixture(oversize, exact_count_authorized=True).issues
        }
        self.assertIn("curve.certificate.exact_oversize", oversize_codes)

        oversized_j0 = deepcopy(self.catalog["fixtures"][2])
        oversized_j0["field_p"] = 65537
        oversized_j0["field_bits"] = 17
        oversized_j0_codes = {
            issue.code
            for issue in validate_fixture(
                oversized_j0, exact_count_authorized=True
            ).issues
        }
        self.assertIn("curve.certificate.exact_oversize", oversized_j0_codes)

        p_plus_one = deepcopy(self.catalog["fixtures"][2])
        p_plus_one["cofactor"] = 7
        p_plus_one["full_order"] = 7 * p_plus_one["subgroup_order"]
        p_plus_one_codes = {
            issue.code
            for issue in validate_fixture(p_plus_one, exact_count_authorized=True).issues
        }
        self.assertIn("curve.certificate.j0_p_plus_one", p_plus_one_codes)

    def test_each_family_claim_rejects_endomorphism_or_property_corruption(self) -> None:
        cases = (
            ("glv_beta", 0, ("endomorphism", "beta"), lambda old: old + 1, "curve.family.glv"),
            ("glv_lambda", 0, ("endomorphism", "lambda"), lambda old: old + 1, "curve.family.glv"),
            ("glv_status", 0, ("endomorphism", "status"), "claimed", "curve.family.glv"),
            (
                "generic_j_property",
                1,
                ("family_property", "j_invariant"),
                0,
                "curve.family.generic_j",
            ),
            (
                "generic_endomorphism",
                1,
                ("endomorphism", "beta"),
                1,
                "curve.family.generic_j",
            ),
            (
                "no_fp_beta",
                2,
                ("endomorphism", "beta"),
                1,
                "curve.family.no_fp_glv",
            ),
            (
                "no_fp_lambda",
                2,
                ("endomorphism", "lambda"),
                1,
                "curve.family.no_fp_glv",
            ),
            (
                "no_fp_reason",
                2,
                ("endomorphism", "reason"),
                "no_endomorphisms_anywhere",
                "curve.family.no_fp_glv",
            ),
            (
                "no_fp_scope",
                2,
                ("family_property", "claim_scope"),
                "all_extensions",
                "curve.family.no_fp_glv",
            ),
        )
        for name, index, path, value, expected in cases:
            with self.subTest(name=name):
                self.assertIn(expected, self.fixture_codes(index, path, value))

    def test_catalog_shape_coverage_limits_and_search_receipts_are_closed(self) -> None:
        mutations: tuple[tuple[str, Callable[[dict[str, Any]], None], str], ...] = (
            ("count", lambda value: value.update({"curve_count": 5}), "curve.catalog.count"),
            (
                "missing_fixture",
                lambda value: value["fixtures"].pop(),
                "curve.catalog.count",
            ),
            (
                "wrong_order",
                lambda value: value["fixtures"].reverse(),
                "curve.catalog.coverage",
            ),
            (
                "duplicate_id",
                lambda value: value["fixtures"][1].update(
                    {"fixture_id": value["fixtures"][0]["fixture_id"]}
                ),
                "curve.catalog.duplicate",
            ),
            (
                "unhashable_id",
                lambda value: value["fixtures"][0].update({"fixture_id": []}),
                "curve.catalog.duplicate",
            ),
            (
                "limit_drift",
                lambda value: value["limits"].update({"max_point_attempts": 1023}),
                "curve.catalog.limits",
            ),
            (
                "zero_search",
                lambda value: value["fixtures"][0]["generation_search"].update(
                    {"point_attempts": 0}
                ),
                "curve.catalog.search",
            ),
            (
                "boolean_search",
                lambda value: value["fixtures"][0]["generation_search"].update(
                    {"point_attempts": True}
                ),
                "curve.catalog.search",
            ),
            (
                "observation",
                lambda value: value.update({"wall_time_seconds": 0}),
                "curve.catalog.observation",
            ),
            (
                "unknown_field",
                lambda value: value.update({"unregistered": True}),
                "curve.catalog.shape",
            ),
        )
        for name, mutation, expected in mutations:
            with self.subTest(name=name):
                catalog = deepcopy(self.catalog)
                mutation(catalog)
                result = validate_catalog_bytes(
                    render(catalog), expected_spec_sha256=self.spec_sha256
                )
                self.assertIn(expected, {issue.code for issue in result.issues})

    def test_strict_ci_json_rejects_duplicate_float_and_nonfinite_numbers(self) -> None:
        raw = CI_CATALOG.read_bytes()
        mutations = (
            raw.replace(b"{\n", b'{\n  "curve_count": 6,\n', 1),
            raw.replace(b'"curve_count": 6', b'"curve_count": 6.0', 1),
            raw.replace(b'"curve_count": 6', b'"curve_count": NaN', 1),
        )
        for mutated in mutations:
            with self.subTest(prefix=mutated[:40]):
                result = validate_catalog_bytes(
                    mutated, expected_spec_sha256=self.spec_sha256
                )
                self.assertIn("curve.catalog.json", {issue.code for issue in result.issues})

    def test_oversized_fixture_array_is_rejected_before_any_curve_arithmetic(self) -> None:
        oversized = deepcopy(self.catalog)
        oversized["fixtures"].append(deepcopy(oversized["fixtures"][0]))
        with patch(
            "experiments.ecdlp_lab.curves.validate_catalog.validate_fixture",
            side_effect=AssertionError("oversized array reached curve validation"),
        ):
            result = validate_catalog_bytes(
                render(oversized), expected_spec_sha256=self.spec_sha256
            )
        self.assertFalse(result.passed)
        self.assertEqual(result.fixture_count, 0)
        self.assertIn("curve.catalog.count", {issue.code for issue in result.issues})

    def test_wrong_spec_authority_never_unlocks_exact_certificates(self) -> None:
        result = validate_catalog_bytes(
            CI_CATALOG.read_bytes(), expected_spec_sha256="f" * 64
        )
        codes = {issue.code for issue in result.issues}
        self.assertIn("curve.catalog.spec", codes)
        self.assertIn("curve.certificate.exact_unauthorized", codes)

    def test_legacy_digest_duplicate_and_overflow_float_corruption_fail_closed(self) -> None:
        raw = LEGACY_CATALOG.read_bytes()
        digest_result = validate_legacy_catalog_bytes(
            raw + b"\n", expected_catalog_sha256=sha256_file(LEGACY_CATALOG)
        )
        self.assertIn("curve.legacy.digest", {issue.code for issue in digest_result.issues})

        duplicate = raw.replace(b"{\n", b'{\n  "schema_version": 1,\n', 1)
        duplicate_result = validate_legacy_catalog_bytes(
            duplicate, expected_catalog_sha256=sha256_bytes(duplicate)
        )
        self.assertIn("curve.legacy.json", {issue.code for issue in duplicate_result.issues})

        overflow = raw.replace(b"0.1801400679978542", b"1e999", 1)
        overflow_result = validate_legacy_catalog_bytes(
            overflow, expected_catalog_sha256=sha256_bytes(overflow)
        )
        self.assertIn("curve.legacy.json", {issue.code for issue in overflow_result.issues})

        changed_order = raw.replace(b'"group_order": 5827', b'"group_order": 5829', 1)
        changed_result = validate_legacy_catalog_bytes(
            changed_order, expected_catalog_sha256=sha256_bytes(changed_order)
        )
        self.assertIn(
            "curve.legacy.payload_digest", {issue.code for issue in changed_result.issues}
        )


if __name__ == "__main__":
    unittest.main()
