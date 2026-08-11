from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from experiments.ecdlp_lab.core.paths import (
    PathSafetyError,
    reject_engine_destination,
    resolve_artifact_path,
    validate_repo_relative,
)


class ArtifactPathBoundaryTests(unittest.TestCase):
    def test_safe_locator_is_preserved_not_normalized(self) -> None:
        locator = "experiments/ecdlp_lab/artifacts/sha256/ab/result.json"
        self.assertEqual(validate_repo_relative(locator), locator)

    def test_traversal_absolute_and_backslash_paths_are_rejected(self) -> None:
        unsafe = (
            "../outside.json",
            "safe/../outside.json",
            "/tmp/outside.json",
            "C:/outside.json",
            r"safe\outside.json",
        )
        for locator in unsafe:
            with self.subTest(locator=locator):
                with self.assertRaises(PathSafetyError):
                    validate_repo_relative(locator)

    def test_engine_destinations_are_rejected_case_insensitively(self) -> None:
        for locator in (
            "experiments/engine/runs/lab.json",
            "experiments/ENGINE/outcomes/lab.json",
            "engine/proposals/lab.json",
        ):
            with self.subTest(locator=locator):
                with self.assertRaisesRegex(PathSafetyError, "Engine"):
                    reject_engine_destination(locator)
                with self.assertRaises(PathSafetyError):
                    validate_repo_relative(locator)

    def test_symlink_component_is_rejected_before_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as root_name, tempfile.TemporaryDirectory() as outside_name:
            root = Path(root_name)
            outside = Path(outside_name)
            link = root / "artifact-link"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except (NotImplementedError, OSError) as error:
                self.skipTest(f"symlinks are unavailable: {error}")
            with self.assertRaisesRegex(PathSafetyError, "symlink"):
                resolve_artifact_path(root, "artifact-link/result.json")

    def test_existing_safe_artifact_resolves_below_root(self) -> None:
        with tempfile.TemporaryDirectory() as root_name:
            root = Path(root_name)
            artifact = root / "artifacts" / "result.json"
            artifact.parent.mkdir()
            artifact.write_text("{}", encoding="utf-8")
            resolved = resolve_artifact_path(
                root, "artifacts/result.json", must_exist=True
            )
            self.assertEqual(resolved, artifact.resolve())
            self.assertEqual(os.path.commonpath((root.resolve(), resolved)), str(root.resolve()))


if __name__ == "__main__":
    unittest.main()
