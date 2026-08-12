from __future__ import annotations

import ast
import json
import shutil
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from experiments.ecdlp_lab.core import legacy_solver_replay as replay
from experiments.ecdlp_lab.core.canonical import (
    load_json,
    sha256_file,
    sha256_json,
)
from experiments.ecdlp_lab.core.issues import Issue


REPO_ROOT = Path(__file__).resolve().parents[3]
LOCATOR = REPO_ROOT / replay.LOCATOR_PATH

_REPLAY_FILES = (
    replay.LOCATOR_PATH,
    "experiments/ecdlp_lab/fixtures/curves/catalog_registry_v1.json",
    "experiments/ecdlp_lab/fixtures/curves/ci_catalog_spec_v1.json",
    "experiments/ecdlp_lab/fixtures/curves/ci_curve_catalog_v1.json",
    "experiments/ecdlp_lab/fixtures/contracts/valid/method_result_v1.json",
    "experiments/ml_structure_probe/reports/p1_toy_scaling/curve_catalog.json",
    "experiments/ml_structure_probe/reports/p1_toy_scaling/assay_result.json",
    "experiments/ml_structure_probe/p1_toy_scaling/run_assay.py",
    "experiments/framework/ec_oracle.py",
)


def copy_replay_repository(destination: Path) -> None:
    for relative_path in _REPLAY_FILES:
        source = REPO_ROOT.joinpath(*relative_path.split("/"))
        target = destination.joinpath(*relative_path.split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def all_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        keys.update(value)
        for child in value.values():
            keys.update(all_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(all_keys(child))
    return keys


class LegacyReplayLoaderTests(unittest.TestCase):
    def test_locator_raw_and_semantic_checksums_are_distinct_and_frozen(self) -> None:
        locator = load_json(LOCATOR)
        self.assertEqual(
            sha256_file(LOCATOR),
            "56f21ebfdcf12e11ebeb803d230883fd143852c10572fd3dbe0253e3eddf058a",
        )
        self.assertEqual(sha256_file(LOCATOR), replay.LOCATOR_RAW_SHA256)
        self.assertEqual(
            sha256_json(locator),
            "d5b1295f7e02aa3829aaa680786b9f39896f6dc77df0b8a5cec7828e6b39380d",
        )
        self.assertEqual(sha256_json(locator), replay.LOCATOR_SEMANTIC_SHA256)
        self.assertNotEqual(sha256_file(LOCATOR), replay.LOCATOR_SEMANTIC_SHA256)
        self.assertNotIn(
            "4c575eb7f69a52ac29e71da5861c3329bf5108c1c58469411464111f5708ec2e",
            json.dumps(locator, sort_keys=True),
        )

    def test_locator_contains_no_answer_target_or_source_row(self) -> None:
        locator = load_json(LOCATOR)
        forbidden = {
            "expected_scalar",
            "candidate_scalar",
            "legacy_candidate_scalar",
            "Q",
            "target",
            "record_index",
            "sample_ordinal",
            "curve_index",
            "generator_index",
        }
        self.assertTrue(forbidden.isdisjoint(all_keys(locator)))
        self.assertFalse(locator["schema_only_quarantine"]["eligible_for_conformance"])
        self.assertEqual(
            locator["schema_only_quarantine"]["p03_expected_counters"],
            {
                "estimated_algorithmic_table_bytes": 4928,
                "legacy_p1_group_operations": 88,
                "method_self_check_group_law_invocations": 2,
                "offline_setup_group_law_invocations": 88,
                "online_target_group_law_invocations": 0,
                "table_entries": 77,
            },
        )

    def test_report_freezes_exact_join_and_aggregate_anchors(self) -> None:
        report = replay.validate_legacy_replay()
        self.assertTrue(report.passed, report.issues)
        self.assertEqual(report.issues, ())
        self.assertTrue(all(isinstance(issue, Issue) for issue in report.issues))
        self.assertEqual(report.case_count, 64)
        self.assertEqual(report.success_count, 64)
        self.assertEqual(report.locator_raw_sha256, replay.LOCATOR_RAW_SHA256)
        self.assertEqual(
            report.locator_semantic_sha256,
            replay.LOCATOR_SEMANTIC_SHA256,
        )
        self.assertEqual((report.bsgs_case_count, report.rho_case_count), (32, 32))
        self.assertEqual(report.bsgs_legacy_group_operations, 61574)
        self.assertEqual(report.bsgs_offline_setup_group_law_invocations, 38739)
        self.assertEqual(report.bsgs_online_target_group_law_invocations, 22835)
        self.assertEqual(report.bsgs_table_entries, 38273)
        self.assertEqual(report.bsgs_estimated_algorithmic_table_bytes, 2449472)
        self.assertEqual(report.rho_legacy_group_operations, 173236)
        self.assertEqual(report.expected_rho_floyd_iterations, 57193)
        self.assertEqual(report.expected_rho_restarts, 0)
        self.assertEqual(report.expected_rho_collisions, 32)
        self.assertEqual(report.expected_rho_noninvertible_collisions, 0)
        self.assertEqual(report.expected_rho_invalid_candidate_collisions, 0)
        self.assertTrue(report.schema_only_quarantine_verified)

    def test_assay_digest_is_checked_before_legacy_parser(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            copy_replay_repository(root)
            assay = root / (
                "experiments/ml_structure_probe/reports/"
                "p1_toy_scaling/assay_result.json"
            )
            assay.write_bytes(assay.read_bytes() + b"\n")
            with patch.object(replay, "_safe_legacy_json") as parser:
                with self.assertRaisesRegex(
                    replay.LegacyReplayError, "raw file digest mismatch"
                ):
                    replay.load_legacy_replay(repo_root=root)
                parser.assert_not_called()

    def test_locator_drift_fails_before_any_source_read(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            copy_replay_repository(root)
            locator_path = root / replay.LOCATOR_PATH
            locator = load_json(locator_path)
            locator["golden"]["case_count"] = 63
            locator_path.write_text(
                json.dumps(locator, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with patch.object(replay, "_read_verified") as source_reader:
                with self.assertRaisesRegex(replay.LegacyReplayError, "raw checksum"):
                    replay.load_legacy_replay(repo_root=root)
                source_reader.assert_not_called()

    def test_legacy_parser_retains_only_finite_observations(self) -> None:
        parsed = replay._safe_legacy_json(b'{"wall":0.25}', label="test")
        self.assertEqual(parsed, {"wall": Decimal("0.25")})
        with self.assertRaisesRegex(replay.LegacyReplayError, "duplicate"):
            replay._safe_legacy_json(b'{"value":1,"value":2}', label="test")
        with self.assertRaisesRegex(replay.LegacyReplayError, "non-finite"):
            replay._safe_legacy_json(b'{"value":NaN}', label="test")

    def test_loader_never_imports_the_heavy_legacy_runner(self) -> None:
        source = Path(replay.__file__).read_text(encoding="utf-8")
        imports: set[str] = set()
        for node in ast.walk(ast.parse(source, filename=replay.__file__)):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module or "")
        self.assertFalse(
            any(
                name == "experiments.ml_structure_probe.p1_toy_scaling.run_assay"
                or name.endswith(".run_assay")
                for name in imports
            )
        )
        self.assertTrue(
            {
                "numpy",
                "scipy",
                "sklearn",
            }.isdisjoint(imports)
        )


if __name__ == "__main__":
    unittest.main()
