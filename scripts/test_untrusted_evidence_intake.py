#!/usr/bin/env python3
"""Fault-injection tests for the quarantined Opus atlas intake."""

from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from build_untrusted_evidence_intake import (
    CONTRACT_PATH,
    ROOT,
    IntakeError,
    analyze_atlas,
    append_only_receipt_problems,
    build_state,
    forbidden_consumer_references,
    load_json_strict,
    loads_strict,
    quarantine_reference_tokens,
    scan_forbidden_consumers,
    validate_contract,
    validation_problems,
)


class UntrustedEvidenceIntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = validate_contract(load_json_strict(CONTRACT_PATH))
        cls.state = build_state(cls.contract)
        source_dir = ROOT / cls.contract["source_directory"]
        cls.mechanisms = load_json_strict(source_dir / "all_mechanisms.json")
        cls.properties = load_json_strict(source_dir / "all_properties.json")
        cls.report_bytes = (source_dir / "ECDLP_SCREEN_ATLAS_REPORT.md").read_bytes()

    def analyze(self, mechanisms=None, properties=None):
        return analyze_atlas(
            self.mechanisms if mechanisms is None else mechanisms,
            self.properties if properties is None else properties,
            self.report_bytes,
            tp_pattern=self.contract["parsing_contract"]["tp_like_reference_pattern"],
        )

    def test_reviewed_counts_and_join_absence_are_exact(self) -> None:
        observations = self.state["observations"]
        self.assertEqual(35, observations["mechanisms"])
        self.assertEqual(223, observations["properties"])
        self.assertEqual(122, observations["requirement_strings"])
        self.assertEqual(12, observations["tp_like_requirement_strings"])
        self.assertEqual(6, observations["unique_orphan_tp_like_references"])
        self.assertEqual(0, observations["verified_join_rows"])
        self.assertEqual("not_present", self.state["join_assessment"]["join_status"])
        self.assertFalse(self.state["join_assessment"]["verified_join"])

    def test_type_violations_and_full_text_discrepancy_are_retained(self) -> None:
        observations = self.state["observations"]
        self.assertEqual(16, observations["declared_integer_parse_violations"])
        self.assertEqual(4, observations["declared_boolean_parse_violations"])
        self.assertEqual(20, observations["declared_type_parse_violations"])
        self.assertEqual(19, observations["mechanism_full_text_read_rows"])
        self.assertEqual(20, observations["report_claimed_full_text_read_rows"])
        self.assertEqual(
            20,
            len(self.state["validation_findings"]["declared_type_parse_violations"]),
        )

    def test_all_authority_and_canonical_effects_remain_zero(self) -> None:
        self.assertTrue(all(value == 0 for value in self.state["authority"].values()))
        for key, value in self.state["canonical_import_plan"].items():
            if key != "next_step":
                self.assertEqual(0, value)
        self.assertFalse(self.state["safety"]["safe_for_scientific_selection"])
        self.assertFalse(self.state["safety"]["safe_for_calibration"])
        self.assertFalse(self.state["safety"]["safe_for_authorization"])
        self.assertEqual(
            [],
            self.state["safety"]["negative_dependency_scan"][
                "prohibited_consumer_references"
            ],
        )

    def test_duplicate_json_keys_are_rejected(self) -> None:
        with self.assertRaisesRegex(IntakeError, "duplicate JSON key"):
            loads_strict('{"same":1,"same":2}', label="fault")

    def test_non_finite_json_numbers_are_rejected(self) -> None:
        with self.assertRaisesRegex(IntakeError, "non-finite JSON number"):
            loads_strict('{"value":NaN}', label="fault")

    def test_invalid_source_hash_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.contract)
        mutated["sources"][0]["sha256"] = "0" * 64
        with patch(
            "build_untrusted_evidence_intake.validate_protected_main_receipt"
        ):
            with self.assertRaisesRegex(IntakeError, "source hash mismatch"):
                build_state(mutated)

    def test_invalid_source_git_blob_hash_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.contract)
        mutated["sources"][0]["git_blob_sha1"] = "0" * 40
        with patch(
            "build_untrusted_evidence_intake.validate_protected_main_receipt"
        ):
            with self.assertRaisesRegex(
                IntakeError, "source Git blob hash mismatch"
            ):
                build_state(mutated)

    def test_parsing_contract_semantics_are_closed(self) -> None:
        for field in ("join_rule", "source_status_rule"):
            with self.subTest(field=field):
                mutated = copy.deepcopy(self.contract)
                mutated["parsing_contract"][field] = "trust the source annotation"
                with self.assertRaisesRegex(
                    IntakeError, "parsing_contract semantics drifted"
                ):
                    validate_contract(mutated)

    def test_protected_main_receipt_freezes_reviewed_source_fields(self) -> None:
        current = copy.deepcopy(self.contract)
        current["sources"][0]["sha256"] = "0" * 64
        self.assertIn(
            "protected-main receipt drifted: sources",
            append_only_receipt_problems(current, self.contract),
        )

    def test_build_state_enforces_protected_main_receipt(self) -> None:
        mutated = copy.deepcopy(self.contract)
        mutated["sources"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(
            IntakeError, "protected-main receipt drifted: sources"
        ):
            build_state(mutated)

    def test_quarantine_reference_in_scientific_consumer_is_rejected(self) -> None:
        references = forbidden_consumer_references(
            {
                "scripts/hypothesis_ranker.py": (
                    'Path("data/untrusted_evidence_intake/atlas.json").read_text()'
                )
            }
        )
        self.assertEqual(["scripts/hypothesis_ranker.py"], references)

    def test_direct_archive_read_in_experiment_is_rejected(self) -> None:
        references = forbidden_consumer_references(
            {
                "experiments/candidate/run.py": (
                    'Path("archive/untrusted_intake/'
                    'OPUS-ECDLP-SCREEN-ATLAS-2026-07-26/'
                    'all_properties.json").read_text()'
                )
            },
            reference_tokens=quarantine_reference_tokens(self.contract),
        )
        self.assertEqual(["experiments/candidate/run.py"], references)

    def test_segmented_windows_archive_path_is_rejected(self) -> None:
        references = forbidden_consumer_references(
            {
                "experiments/candidate/run.ps1": (
                    "$p = 'archive' + '\\untrusted_intake' + "
                    "'\\OPUS-ECDLP-SCREEN-ATLAS-2026-07-26' + "
                    "'\\all_mechanisms.json'"
                )
            },
            reference_tokens=quarantine_reference_tokens(self.contract),
        )
        self.assertEqual(["experiments/candidate/run.ps1"], references)

    def test_experiments_root_and_shell_suffix_are_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            consumer = root / "experiments" / "candidate" / "run.sh"
            consumer.parent.mkdir(parents=True)
            consumer.write_text(
                "cat archive/untrusted_intake/"
                "OPUS-ECDLP-SCREEN-ATLAS-2026-07-26/all_properties.json\n",
                encoding="utf-8",
            )
            self.assertEqual(
                ["experiments/candidate/run.sh"],
                scan_forbidden_consumers(root=root, contract=self.contract),
            )

    def test_current_tree_has_no_scientific_consumer_reference(self) -> None:
        self.assertEqual([], scan_forbidden_consumers())

    def test_generated_source_hash_drift_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.state)
        mutated["source_artifacts"][0]["sha256"] = "0" * 64
        self.assertIn(
            "source artifact binding drifted",
            validation_problems(mutated, self.contract),
        )

    def test_raw_values_cannot_be_coerced_to_json_scalars(self) -> None:
        mutated = copy.deepcopy(self.properties)
        mutated["TP-F03"]["value"] = True
        with self.assertRaisesRegex(IntakeError, "must remain a raw string"):
            self.analyze(properties=mutated)

    def test_duplicate_mechanism_id_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.mechanisms)
        mutated[1]["id"] = mutated[0]["id"]
        with self.assertRaisesRegex(IntakeError, "duplicate mechanism id"):
            self.analyze(mechanisms=mutated)

    def test_property_key_id_mismatch_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.properties)
        mutated["TP-F01"]["id"] = "TP-WRONG"
        with self.assertRaisesRegex(IntakeError, "does not match its object key"):
            self.analyze(properties=mutated)

    def test_authority_drift_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.state)
        mutated["authority"]["ranker_labels"] = 1
        problems = validation_problems(mutated, self.contract)
        self.assertIn("authority ceiling drifted", problems)
        self.assertIn("untrusted intake acquired nonzero authority", problems)

    def test_boolean_false_cannot_impersonate_integer_zero(self) -> None:
        mutated = copy.deepcopy(self.state)
        mutated["authority"]["authorization"] = False
        problems = validation_problems(mutated, self.contract)
        self.assertIn("untrusted intake acquired nonzero authority", problems)

    def test_output_path_cannot_escape_quarantine(self) -> None:
        mutated = copy.deepcopy(self.contract)
        mutated["output_path"] = "../repo/ECDLP_TYPED_EVIDENCE_V0.json"
        with self.assertRaisesRegex(IntakeError, "output_path"):
            validate_contract(mutated)

    def test_verified_join_claim_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.state)
        mutated["join_assessment"]["join_status"] = "verified"
        mutated["join_assessment"]["verified_join"] = True
        self.assertIn(
            "untrusted atlas was treated as a verified join",
            validation_problems(mutated, self.contract),
        )

    def test_scientific_selection_or_authorization_is_rejected(self) -> None:
        for key in (
            "safe_for_scientific_selection",
            "safe_for_calibration",
            "safe_for_authorization",
        ):
            mutated = copy.deepcopy(self.state)
            mutated["safety"][key] = True
            self.assertIn(f"{key} must remain false", validation_problems(mutated, self.contract))

    def test_source_records_are_catalogued_by_pointer_and_digest(self) -> None:
        self.assertEqual(35, len(self.state["mechanism_envelopes"]))
        self.assertEqual(223, len(self.state["property_candidates"]))
        self.assertEqual(122, len(self.state["requirement_annotations"]))
        for record in self.state["mechanism_envelopes"]:
            self.assertRegex(
                record["canonical_record_sha256"], r"^[0-9a-f]{64}$"
            )
            self.assertNotIn("raw_record_sha256", record)
            self.assertEqual("untrusted_mechanism_envelope", record["classification"])
        for record in self.state["property_candidates"]:
            self.assertRegex(
                record["canonical_record_sha256"], r"^[0-9a-f]{64}$"
            )
            self.assertNotIn("raw_record_sha256", record)


if __name__ == "__main__":
    unittest.main()
