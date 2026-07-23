#!/usr/bin/env python3
"""Regression tests for the candidate-evaluation contract."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from candidate_contract import (
    REQUIRED_TOP_LEVEL,
    canonical_hash,
    load_decisions,
    load_record,
    record_payload,
    validate_record,
)
from ec_oracle import Curve

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"


class FrameworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decisions = load_decisions(ROOT)

    def test_valid_fixture(self) -> None:
        record = load_record(FIXTURES / "valid.json")
        self.assertEqual([], validate_record(record, self.decisions))

    def test_invalid_fixtures_fail_for_the_intended_reason(self) -> None:
        cases = {
            "invalid_hidden_precomputation.json": (
                "plain threat model forbids reusable precomputation"
            ),
            "invalid_self_validation.json": (
                "validator must be marked as an independent implementation"
            ),
            "invalid_wrong_output.json": (
                "claimed scalar does not reproduce the target point"
            ),
            "invalid_missing_provenance.json": (
                "provenance.environment_sha256 must be a lowercase SHA-256 hex digest"
            ),
        }
        for filename, expected in cases.items():
            with self.subTest(filename=filename):
                errors = validate_record(
                    load_record(FIXTURES / filename), self.decisions
                )
                self.assertTrue(errors)
                self.assertIn(expected, errors)

    def test_real_run_is_rejected_until_route_selection(self) -> None:
        record = copy.deepcopy(load_record(FIXTURES / "valid.json"))
        record["record_kind"] = "candidate_run"
        record["provenance"]["record_sha256"] = canonical_hash(record_payload(record))
        errors = validate_record(record, self.decisions)
        self.assertIn(
            "route R-GENERIC-BASELINE does not authorize a candidate run", errors
        )

    def test_oracle_known_multiples(self) -> None:
        curve = Curve(17, 0, 7)
        base = (1, 5)
        self.assertEqual((12, 16), curve.scalar_mul(5, base))
        self.assertIsNone(curve.scalar_mul(9, base))

    def test_schema_and_semantic_validator_share_top_level_contract(self) -> None:
        schema = json.loads(
            (HERE / "candidate_run.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(REQUIRED_TOP_LEVEL, set(schema["required"]))
        self.assertIn("record_sha256", schema["properties"]["provenance"]["required"])

    def test_record_hash_covers_provenance_and_validation(self) -> None:
        for field, value in (
            (("provenance", "command"), ["changed-command"]),
            (("validation", "independent_implementation"), False),
        ):
            with self.subTest(field=field):
                record = copy.deepcopy(load_record(FIXTURES / "valid.json"))
                record[field[0]][field[1]] = value
                errors = validate_record(record, self.decisions)
                self.assertIn(
                    "provenance.record_sha256 does not match the canonical payload",
                    errors,
                )

    def test_empty_command_and_unknown_field_are_rejected(self) -> None:
        record = copy.deepcopy(load_record(FIXTURES / "valid.json"))
        record["provenance"]["command"] = []
        record["candidate"]["undeclared"] = "not allowed"
        record["provenance"]["record_sha256"] = canonical_hash(record_payload(record))
        errors = validate_record(record, self.decisions)
        self.assertIn("provenance.command must be a nonempty string array", errors)
        self.assertIn("candidate has unknown fields: ['undeclared']", errors)

    def test_route_scope_and_hypothesis_binding_are_enforced(self) -> None:
        record = copy.deepcopy(load_record(FIXTURES / "valid.json"))
        record["target"]["threat_model"] = "fault-tolerant-quantum"
        record["candidate"]["hypothesis_id"] = "HYP_WARD_EDS_001"
        record["provenance"]["input_sha256"] = canonical_hash(record["target"])
        record["provenance"]["record_sha256"] = canonical_hash(record_payload(record))
        errors = validate_record(record, self.decisions)
        self.assertIn(
            "target.threat_model 'fault-tolerant-quantum' is not declared for route "
            "R-GENERIC-BASELINE",
            errors,
        )
        self.assertIn(
            "candidate.hypothesis_id 'HYP_WARD_EDS_001' is not bound to route "
            "R-GENERIC-BASELINE",
            errors,
        )

    def test_oracle_rejects_composite_fields_and_inexact_orders(self) -> None:
        for field_p, order, expected in (
            (15, 9, "the oracle requires a prime field with p > 3"),
            (17, 18, "target.base_order is not the exact base-point order"),
        ):
            with self.subTest(field_p=field_p, order=order):
                record = copy.deepcopy(load_record(FIXTURES / "valid.json"))
                record["target"]["field_p"] = field_p
                record["target"]["base_order"] = order
                record["provenance"]["input_sha256"] = canonical_hash(record["target"])
                record["provenance"]["record_sha256"] = canonical_hash(
                    record_payload(record)
                )
                errors = validate_record(record, self.decisions)
                self.assertTrue(
                    any(expected in error for error in errors),
                    msg=f"{expected!r} not found in {errors!r}",
                )


if __name__ == "__main__":
    unittest.main()
