from __future__ import annotations

import unittest
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
import tempfile
from typing import Any

from experiments.ecdlp_lab.core.canonical import StrictJSONError, load_json, strict_loads
from experiments.ecdlp_lab.core.contracts import ValidationContext, validate_contract
from experiments.ecdlp_lab.core.schema import validate_schema


REPO_ROOT = Path(__file__).resolve().parents[3]
LAB_ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = LAB_ROOT / "fixtures" / "contracts" / "invalid_cases_v1.json"
SCHEMA_ROOT = LAB_ROOT / "contracts"

REQUIRED_CASES = {
    "unknown_field",
    "malformed_digest",
    "absolute_path",
    "parent_path_escape",
    "symlink_escape",
    "missing_provenance",
    "dirty_record_marked_retainable",
    "self_validation",
    "hidden_precomputation",
    "expected_scalar_leak",
    "target_seed_leak",
    "science_identifiers",
    "attempted_engine_conversion",
    "native_research_outcome",
    "subgroup_bits_over_32",
    "exact_secp256k1_parameters",
    "external_target_point",
    "unknown_catalog_digest",
    "unknown_vector_digest",
    "floating_point_counter",
    "nan_lexeme",
    "infinity_lexeme",
    "negative_zero_lexeme",
    "duplicate_key",
}


def _parts(pointer: str) -> list[str]:
    if pointer in ("", "/"):
        return []
    if not pointer.startswith("/"):
        raise AssertionError(f"invalid fixture pointer: {pointer!r}")
    return [item.replace("~1", "/").replace("~0", "~") for item in pointer[1:].split("/")]


def _lookup(document: Any, pointer: str) -> Any:
    value = document
    for part in _parts(pointer):
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def _assign(document: Any, pointer: str, value: Any) -> None:
    parts = _parts(pointer)
    if not parts:
        if not isinstance(document, dict) or not isinstance(value, dict):
            raise AssertionError("root mutation must merge objects")
        document.update(value)
        return
    parent = document
    for part in parts[:-1]:
        parent = parent[int(part)] if isinstance(parent, list) else parent[part]
    last = parts[-1]
    if isinstance(parent, list):
        parent[int(last)] = value
    else:
        parent[last] = value


def apply_mutation(document: dict[str, Any], mutation: dict[str, Any]) -> dict[str, Any]:
    mutated = deepcopy(document)
    operation = mutation["operation"]
    pointer = mutation["pointer"]
    if operation in {"add", "replace"}:
        _assign(mutated, pointer, mutation["value"])
    elif operation == "replace_many":
        target = _lookup(mutated, pointer)
        if not isinstance(target, dict) or not isinstance(mutation["value"], dict):
            raise AssertionError("replace_many must target and supply objects")
        target.update(mutation["value"])
    elif operation == "copy":
        _assign(mutated, pointer, deepcopy(_lookup(mutated, mutation["value"])))
    elif operation == "remove":
        parts = _parts(pointer)
        parent: Any = mutated
        for part in parts[:-1]:
            parent = parent[int(part)] if isinstance(parent, list) else parent[part]
        del parent[parts[-1]]
    else:
        raise AssertionError(f"mutation {operation!r} is not a pure schema mutation")
    return mutated


class AdversarialFixtureCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        manifest = load_json(CASES_PATH)
        if not isinstance(manifest, dict) or not isinstance(manifest.get("cases"), list):
            raise AssertionError("invalid adversarial fixture manifest")
        cls.cases = manifest["cases"]
        cls.case_by_id = {case["case_id"]: case for case in cls.cases}
        cls.valid_records = [
            load_json(path)
            for path in sorted((CASES_PATH.parent / "valid").glob("*.json"))
        ]
        cls.semantic_context = ValidationContext.from_records(
            cls.valid_records,
            repo_root=REPO_ROOT,
            known_catalog_sha256s={
                record["public_payload"]["curve_catalog_sha256"]
                for record in cls.valid_records
                if record.get("contract_kind") == "target_vector_v1"
                and record.get("branch") == "public"
            },
            known_target_vector_sha256s={
                record["target_vector_id"]
                for record in cls.valid_records
                if record.get("contract_kind") == "target_vector_v1"
                and record.get("branch") == "public"
            },
            verify_artifacts=False,
        )

    def test_required_adversarial_cases_are_frozen(self) -> None:
        case_ids = {case["case_id"] for case in self.cases}
        self.assertTrue(REQUIRED_CASES.issubset(case_ids))
        self.assertEqual(len(case_ids), len(self.cases), "duplicate adversarial case_id")

    def test_raw_json_adversaries_fail_strict_parsing(self) -> None:
        raw_cases = [
            case for case in self.cases if case["mutation"]["operation"] == "parse_raw_json"
        ]
        self.assertEqual(
            {case["case_id"] for case in raw_cases},
            {"nan_lexeme", "infinity_lexeme", "negative_zero_lexeme", "duplicate_key"},
        )
        for case in raw_cases:
            with self.subTest(case=case["case_id"]):
                with self.assertRaises(StrictJSONError):
                    strict_loads(case["mutation"]["value"])

    def test_schema_stage_mutations_are_rejected(self) -> None:
        schema_cases = [
            case
            for case in self.cases
            if case["expected_stage"] in {"schema", "schema_or_semantic"}
        ]
        self.assertGreaterEqual(len(schema_cases), 14)
        for case in schema_cases:
            with self.subTest(case=case["case_id"]):
                base = load_json(REPO_ROOT / case["base_fixture"])
                self.assertIsInstance(base, dict)
                mutated = apply_mutation(base, case["mutation"])
                schema = load_json(
                    SCHEMA_ROOT / f"{case['contract_kind']}.schema.json"
                )
                self.assertIsInstance(schema, dict)
                self.assertNotEqual(validate_schema(mutated, schema), [])

    def test_semantic_mutations_fail_the_named_boundary(self) -> None:
        expected_codes = {
            "self_validation": "contract.validation.self_validator",
            "external_target_point": "contract.method_request.target_binding",
            "unknown_catalog_digest": "contract.catalog.unknown",
            "unknown_vector_digest": "contract.target_vector.unknown",
            "expected_scalar_leak": "contract.method_request.private_target",
            "target_seed_leak": "contract.method_request.private_target",
        }
        for case_id, expected_code in expected_codes.items():
            with self.subTest(case=case_id):
                case = self.case_by_id[case_id]
                base = load_json(REPO_ROOT / case["base_fixture"])
                mutated = apply_mutation(base, case["mutation"])
                issues = validate_contract(mutated, self.semantic_context)
                self.assertIn(expected_code, {issue.code for issue in issues})

    def test_artifact_symlink_escape_fails_semantic_resolution(self) -> None:
        case = self.case_by_id["symlink_escape"]
        base = load_json(REPO_ROOT / case["base_fixture"])
        mutated = deepcopy(base)
        _assign(mutated, case["mutation"]["pointer"], case["mutation"]["value"])
        with tempfile.TemporaryDirectory() as root_name, tempfile.TemporaryDirectory() as outside_name:
            root = Path(root_name)
            link = root / "experiments" / "ecdlp_lab" / "fixtures" / "contracts" / "link"
            link.parent.mkdir(parents=True)
            try:
                link.symlink_to(Path(outside_name), target_is_directory=True)
            except (NotImplementedError, OSError) as error:
                self.skipTest(f"symlinks are unavailable: {error}")
            context = replace(
                self.semantic_context,
                repo_root=root,
                verify_artifacts=True,
            )
            issues = validate_contract(mutated, context)
        self.assertIn("contract.artifact.path", {issue.code for issue in issues})

    def test_engine_destination_fails_artifact_semantics(self) -> None:
        artifact = load_json(
            CASES_PATH.parent / "valid" / "artifact_ref_v1.json"
        )
        artifact["location"] = "experiments/engine/runs/lab-result.json"
        issues = validate_contract(artifact, self.semantic_context)
        self.assertIn("contract.artifact.path", {issue.code for issue in issues})

    def test_artifact_bytes_bind_hash_and_size(self) -> None:
        artifact_path = CASES_PATH.parent / "valid" / "artifact_ref_v1.json"
        artifact = load_json(artifact_path)
        context = replace(self.semantic_context, verify_artifacts=True)
        self.assertEqual(validate_contract(artifact, context), [])

        wrong_size = deepcopy(artifact)
        wrong_size["size_bytes"] += 1
        self.assertIn(
            "contract.artifact.size",
            {issue.code for issue in validate_contract(wrong_size, context)},
        )

        wrong_hash = deepcopy(artifact)
        wrong_hash["sha256"] = "0" * 64
        wrong_hash["artifact_id"] = "0" * 64
        self.assertIn(
            "contract.artifact.hash",
            {issue.code for issue in validate_contract(wrong_hash, context)},
        )


if __name__ == "__main__":
    unittest.main()
