#!/usr/bin/env python3
"""Fail-closed mutation tests for the portability rehearsal control gate."""
from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import check_portability_rehearsal as rehearsal_check  # noqa: E402


class PortabilityRehearsalCheckTests(unittest.TestCase):
    def run_with_mutation(self, mutation) -> tuple[int, str]:
        original_load_json = rehearsal_check.load_json

        def load_json(path: Path) -> dict:
            value = copy.deepcopy(original_load_json(path))
            mutation(path, value)
            return value

        stderr = io.StringIO()
        with (
            patch.object(rehearsal_check, "load_json", side_effect=load_json),
            contextlib.redirect_stderr(stderr),
        ):
            result = rehearsal_check.main(require_final=True)
        return result, stderr.getvalue()

    def test_committed_final_rehearsal_passes(self) -> None:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            result = rehearsal_check.main(require_final=True)
        self.assertEqual(result, 0, stderr.getvalue())

    def test_require_final_rejects_in_progress_contract(self) -> None:
        def mutate(path: Path, value: dict) -> None:
            if path == rehearsal_check.CONTRACT_PATH:
                value["status"] = "adapter_in_progress"
                value["decision"] = {
                    "status": "pending",
                    "disposition": None,
                    "performed_on": None,
                    "summary": None,
                    "evidence_files": [],
                }

        result, stderr = self.run_with_mutation(mutate)
        self.assertEqual(result, 1)
        self.assertIn("--require-final rejects an in-progress", stderr)

    def test_required_metric_cannot_be_de_scoped(self) -> None:
        def mutate(path: Path, value: dict) -> None:
            if path == rehearsal_check.CONTRACT_PATH:
                value["metrics"][0]["required_for_build"] = False

        result, stderr = self.run_with_mutation(mutate)
        self.assertEqual(result, 1)
        self.assertIn("every fixed rehearsal metric must remain required", stderr)

    def test_rehashed_compiled_probe_cannot_change_source_binding(self) -> None:
        def mutate(path: Path, value: dict) -> None:
            if path.name == "compiled-probe.json":
                value["source"]["snapshot_sha256"] = "0" * 64
                unsigned = dict(value)
                unsigned.pop("probe_sha256", None)
                value["probe_sha256"] = hashlib.sha256(
                    rehearsal_check.canonical_json_bytes(unsigned)
                ).hexdigest()

        result, stderr = self.run_with_mutation(mutate)
        self.assertEqual(result, 1)
        self.assertIn("compiled probe source does not match selected source", stderr)

    def test_rehashed_baseline_cannot_claim_external_evidence(self) -> None:
        def mutate(path: Path, value: dict) -> None:
            if path.name == "baseline.json":
                value["external_evidence"] = True
                unsigned = dict(value)
                unsigned.pop("evidence_sha256", None)
                value["evidence_sha256"] = hashlib.sha256(
                    rehearsal_check.canonical_json_bytes(unsigned)
                ).hexdigest()

        result, stderr = self.run_with_mutation(mutate)
        self.assertEqual(result, 1)
        self.assertIn("baseline evidence identity or evidence boundary is invalid", stderr)

    def test_rehashed_snapshot_cannot_duplicate_a_tracked_path(self) -> None:
        def mutate(path: Path, value: dict) -> None:
            if path.name == "snapshot.json":
                matching = [
                    index
                    for index, item in enumerate(value["files"])
                    if item["classification"] == "other"
                ]
                value["files"][matching[1]] = copy.deepcopy(
                    value["files"][matching[0]]
                )
                value["files"].sort(key=lambda item: item["path"])
                value["content_manifest_sha256"] = hashlib.sha256(
                    rehearsal_check.canonical_json_bytes(value["files"])
                ).hexdigest()
                unsigned = dict(value)
                unsigned.pop("snapshot_sha256", None)
                value["snapshot_sha256"] = hashlib.sha256(
                    rehearsal_check.canonical_json_bytes(unsigned)
                ).hexdigest()

        result, stderr = self.run_with_mutation(mutate)
        self.assertEqual(result, 1)
        self.assertIn(
            "snapshot file paths must be safe, unique, and canonically sorted",
            stderr,
        )

    def test_rehashed_snapshot_cannot_forge_git_mode_classification(self) -> None:
        def mutate(path: Path, value: dict) -> None:
            if path.name == "snapshot.json":
                record = next(
                    item
                    for item in value["files"]
                    if item["git_mode"] == "100644"
                    and item["classification"] == "other"
                )
                record["git_mode"] = "120000"
                value["content_manifest_sha256"] = hashlib.sha256(
                    rehearsal_check.canonical_json_bytes(value["files"])
                ).hexdigest()
                unsigned = dict(value)
                unsigned.pop("snapshot_sha256", None)
                value["snapshot_sha256"] = hashlib.sha256(
                    rehearsal_check.canonical_json_bytes(unsigned)
                ).hexdigest()

        result, stderr = self.run_with_mutation(mutate)
        self.assertEqual(result, 1)
        self.assertIn(
            "snapshot Git mode, object type, classification, and file module",
            stderr,
        )

    def test_rehashed_snapshot_cannot_rename_adapter_derived_module(self) -> None:
        def mutate(path: Path, value: dict) -> None:
            if path.name == "snapshot.json":
                module = next(
                    item
                    for item in value["modules"]
                    if item["module"] == "UnitTest"
                )
                file_record = next(
                    item
                    for item in value["files"]
                    if item.get("module") == "UnitTest"
                )
                module["module"] = "Forged.UnitTest"
                file_record["module"] = "Forged.UnitTest"
                value["modules"].sort(key=lambda item: item["module"])
                value["content_manifest_sha256"] = hashlib.sha256(
                    rehearsal_check.canonical_json_bytes(value["files"])
                ).hexdigest()
                unsigned = dict(value)
                unsigned.pop("snapshot_sha256", None)
                value["snapshot_sha256"] = hashlib.sha256(
                    rehearsal_check.canonical_json_bytes(unsigned)
                ).hexdigest()

        result, stderr = self.run_with_mutation(mutate)
        self.assertEqual(result, 1)
        self.assertIn(
            "snapshot module names must derive from file paths and module roots",
            stderr,
        )

    def test_rehashed_baseline_cannot_replace_documented_update_command(self) -> None:
        def mutate(path: Path, value: dict) -> None:
            if path.name == "baseline.json":
                value["dependency_resolution"]["command"] = (
                    "cd cedar-lean && echo forged-update"
                )
                unsigned = dict(value)
                unsigned.pop("evidence_sha256", None)
                value["evidence_sha256"] = hashlib.sha256(
                    rehearsal_check.canonical_json_bytes(unsigned)
                ).hexdigest()

        result, stderr = self.run_with_mutation(mutate)
        self.assertEqual(result, 1)
        self.assertIn(
            "baseline dependency resolution must match the exact contract",
            stderr,
        )

    def test_rehashed_probe_cannot_forge_allowed_axiom_provenance(self) -> None:
        def mutate(path: Path, value: dict) -> None:
            if path.name == "compiled-probe.json":
                propext = next(
                    item
                    for item in value["axiom_provenance"]
                    if item["name"] == "propext"
                )
                propext["module"] = "Init.Prelude"
                unsigned = dict(value)
                unsigned.pop("probe_sha256", None)
                value["probe_sha256"] = hashlib.sha256(
                    rehearsal_check.canonical_json_bytes(unsigned)
                ).hexdigest()

        result, stderr = self.run_with_mutation(mutate)
        self.assertEqual(result, 1)
        self.assertIn(
            "compiled probe trust policy must pass without forbidden or unexpected axioms",
            stderr,
        )

    def test_rehashed_probe_cannot_omit_observed_workspace_change(self) -> None:
        def mutate(path: Path, value: dict) -> None:
            if path.name == "compiled-probe.json":
                value["source"]["observed_workspace_changes"] = []
                unsigned = dict(value)
                unsigned.pop("probe_sha256", None)
                value["probe_sha256"] = hashlib.sha256(
                    rehearsal_check.canonical_json_bytes(unsigned)
                ).hexdigest()

        result, stderr = self.run_with_mutation(mutate)
        self.assertEqual(result, 1)
        self.assertIn(
            "compiled probe workspace changes must exactly match",
            stderr,
        )

    def test_native_decide_trust_class_cannot_be_weakened(self) -> None:
        def mutate(path: Path, value: dict) -> None:
            if path == rehearsal_check.CONTRACT_PATH:
                value["compiled_probe_policy"]["accepted_axiom_groups"][0][
                    "trust_class"
                ] = "project_asserted"

        result, stderr = self.run_with_mutation(mutate)
        self.assertEqual(result, 1)
        self.assertIn(
            "compiled probe must retain the exact native_decide trust group",
            stderr,
        )

    def test_selected_source_cannot_leak_into_product_controls(self) -> None:
        def mutate(path: Path, value: dict) -> None:
            if path == rehearsal_check.PRODUCT_MODEL_PATH:
                value["internal_rehearsal_leak"] = (
                    "https://github.com/cedar-policy/cedar-spec"
                )

        result, stderr = self.run_with_mutation(mutate)
        self.assertEqual(result, 1)
        self.assertIn("rehearsal evidence leaked into pilot, product, or task", stderr)

    def test_reserve_candidate_cannot_leak_into_public_surface(self) -> None:
        original_read_text = Path.read_text
        public_path = ROOT / "CNAME"

        def read_text(path: Path, *args, **kwargs) -> str:
            if path == public_path:
                return "reserve=c48433678e8fb6306ebcd48453300c8e16058a62\n"
            return original_read_text(path, *args, **kwargs)

        stderr = io.StringIO()
        with (
            patch.object(Path, "read_text", new=read_text),
            contextlib.redirect_stderr(stderr),
        ):
            result = rehearsal_check.main(require_final=True)
        self.assertEqual(result, 1)
        self.assertIn("contains internal portability rehearsal evidence", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
