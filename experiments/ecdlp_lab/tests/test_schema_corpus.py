from __future__ import annotations

import unittest
from pathlib import Path
from copy import deepcopy

from experiments.ecdlp_lab.core.canonical import load_json
from experiments.ecdlp_lab.core.schema import schema_definition_issues, validate_schema


LAB_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = LAB_ROOT / "contracts"
VALID_FIXTURE_ROOT = LAB_ROOT / "fixtures" / "contracts" / "valid"
EXPECTED_KINDS = {
    "campaign_config_v1",
    "target_vector_v1",
    "work_unit_v1",
    "method_request_v1",
    "method_result_v1",
    "telemetry_v1",
    "validation_receipt_v1",
    "analysis_summary_v1",
    "artifact_ref_v1",
}


class SchemaCorpusTests(unittest.TestCase):
    @staticmethod
    def schema_for(contract_kind: str) -> dict[str, object]:
        schema = load_json(SCHEMA_ROOT / f"{contract_kind}.schema.json")
        if not isinstance(schema, dict):
            raise AssertionError(f"schema for {contract_kind} is not an object")
        return schema

    def test_exact_nine_versioned_contract_schemas_are_registered(self) -> None:
        schemas = {
            path.name.removesuffix(".schema.json"): path
            for path in SCHEMA_ROOT.glob("*_v1.schema.json")
        }
        self.assertEqual(set(schemas), EXPECTED_KINDS)
        for contract_kind, path in sorted(schemas.items()):
            with self.subTest(contract_kind=contract_kind):
                schema = load_json(path)
                self.assertIsInstance(schema, dict)
                self.assertEqual(
                    schema["properties"]["contract_kind"]["const"], contract_kind
                )
                self.assertEqual(schema.get("additionalProperties"), False)
                self.assertEqual(schema_definition_issues(schema), [])

    def test_committed_positive_corpus_covers_and_validates_every_family(self) -> None:
        seen: set[str] = set()
        fixtures = sorted(VALID_FIXTURE_ROOT.glob("*.json"))
        self.assertGreaterEqual(len(fixtures), len(EXPECTED_KINDS))
        for path in fixtures:
            with self.subTest(fixture=path.name):
                record = load_json(path)
                self.assertIsInstance(record, dict)
                contract_kind = record.get("contract_kind")
                self.assertIn(contract_kind, EXPECTED_KINDS)
                seen.add(contract_kind)
                schema = self.schema_for(contract_kind)
                self.assertEqual(validate_schema(record, schema), [])
        self.assertEqual(seen, EXPECTED_KINDS)

    def test_unknown_top_level_field_is_rejected(self) -> None:
        original = load_json(VALID_FIXTURE_ROOT / "campaign_config_v1.json")
        self.assertIsInstance(original, dict)
        mutated = deepcopy(original)
        mutated["unregistered_override"] = True
        issues = validate_schema(mutated, self.schema_for("campaign_config_v1"))
        self.assertTrue(
            any(
                issue.code == "schema.additional_property"
                and issue.path == "$.unregistered_override"
                for issue in issues
            )
        )

    def test_decimal_string_negative_zero_is_rejected(self) -> None:
        original = load_json(VALID_FIXTURE_ROOT / "analysis_summary_v1.json")
        self.assertIsInstance(original, dict)
        mutated = deepcopy(original)
        mutated["model_fits"][0]["coefficients"] = [
            {"name": "alpha", "value_decimal": "-0.0"}
        ]
        issues = validate_schema(mutated, self.schema_for("analysis_summary_v1"))
        self.assertTrue(any(issue.code == "schema.pattern" for issue in issues))


if __name__ == "__main__":
    unittest.main()
