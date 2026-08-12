from __future__ import annotations

import ast
from contextlib import redirect_stderr
from io import StringIO
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.ecdlp_lab.orchestration import storage
from experiments.ecdlp_lab.orchestration.model import OrchestrationError
from experiments.ecdlp_lab.orchestration.run_smoke import _artifact_root, main
from experiments.ecdlp_lab.orchestration.runner import RunnerError, run_campaign
from experiments.ecdlp_lab.orchestration.storage import ArtifactStore, StorageError


REPO_ROOT = Path(__file__).resolve().parents[3]
ORCHESTRATION = REPO_ROOT / "experiments/ecdlp_lab/orchestration"


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


class P04NoEnginePathTests(unittest.TestCase):
    def test_runner_rejects_every_repository_local_artifact_root_before_write(self) -> None:
        destinations = (
            REPO_ROOT / "experiments/engine/p04-forbidden",
            REPO_ROOT / "data/p04-forbidden",
            REPO_ROOT / "experiments/ecdlp_lab/.work/p04-forbidden",
        )
        for destination in destinations:
            with self.subTest(destination=destination):
                self.assertFalse(destination.exists())
                with self.assertRaisesRegex(RunnerError, "artifact_root"):
                    run_campaign({}, destination, repo_root=REPO_ROOT)
                self.assertFalse(destination.exists())

    def test_cli_accepts_no_configured_module_command_or_repository_output(self) -> None:
        with redirect_stderr(StringIO()):
            self.assertEqual(
                main(
                    [
                        "--config",
                        "../smoke.json",
                        "--output",
                        "/tmp/p04-never-created",
                    ]
                ),
                2,
            )
        with self.assertRaisesRegex(RunnerError, "output"):
            _artifact_root(str(REPO_ROOT / "experiments/engine/p04-forbidden"))

    def test_output_root_rejects_relative_traversal_and_symlink(self) -> None:
        for value in ("relative", "/tmp/../etc/p04", "file:///tmp/p04"):
            with self.subTest(value=value):
                with self.assertRaises(RunnerError):
                    _artifact_root(value)
        with tempfile.TemporaryDirectory(prefix="p04-path-") as raw:
            root = Path(raw)
            link = root / "link"
            try:
                link.symlink_to(root, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            with self.assertRaises(RunnerError):
                _artifact_root(str(link))

    def test_check_to_create_parent_swap_cannot_redirect_into_engine(self) -> None:
        engine = REPO_ROOT / "experiments/engine"
        leaf = "p04-dirfd-race-artifacts"
        self.assertFalse((engine / leaf).exists())
        with tempfile.TemporaryDirectory(prefix="p04-root-race-") as raw:
            base = Path(raw)
            parent = base / "safe-parent"
            moved = base / "moved-parent"
            parent.mkdir()
            destination = parent / leaf
            real_mkdir = storage.os.mkdir
            swapped = False

            def swap_then_mkdir(
                component: str,
                mode: int = 0o777,
                *,
                dir_fd: int | None = None,
            ) -> None:
                nonlocal swapped
                if component == leaf and dir_fd is not None and not swapped:
                    swapped = True
                    parent.rename(moved)
                    parent.symlink_to(engine, target_is_directory=True)
                real_mkdir(component, mode=mode, dir_fd=dir_fd)

            with patch.object(
                storage, "storage_primitives_available", return_value=True
            ), patch.object(storage.os, "mkdir", side_effect=swap_then_mkdir):
                with self.assertRaisesRegex(RunnerError, "artifact_root"):
                    run_campaign({}, destination, repo_root=REPO_ROOT)
            self.assertTrue(swapped)
            self.assertFalse((engine / leaf).exists())
            self.assertFalse((engine / leaf / "events.jsonl").exists())

    def test_bound_store_rejects_intermediate_parent_replacement(self) -> None:
        engine = REPO_ROOT / "experiments/engine"
        leaf = "p04-bound-root-artifacts"
        self.assertFalse((engine / leaf).exists())
        with tempfile.TemporaryDirectory(prefix="p04-bound-race-") as raw:
            base = Path(raw)
            parent = base / "safe-parent"
            moved = base / "moved-parent"
            parent.mkdir()
            store = ArtifactStore(parent / leaf, forbidden_root=REPO_ROOT)
            try:
                parent.rename(moved)
                parent.symlink_to(engine, target_is_directory=True)
                with self.assertRaises(StorageError):
                    store.create_bytes("must-not-land", b"x")
            finally:
                store.close()
            self.assertFalse((engine / leaf).exists())

    def test_cli_sanitizes_config_boundary_failures(self) -> None:
        with tempfile.TemporaryDirectory(prefix="p04-cli-error-") as raw:
            output = Path(raw) / "artifacts"
            diagnostics = StringIO()
            with patch(
                "experiments.ecdlp_lab.orchestration.run_smoke.load_smoke_campaign",
                side_effect=OrchestrationError(
                    "orchestration.config.load", "$.config", "fixture drifted"
                ),
            ), redirect_stderr(diagnostics):
                status = main(
                    [
                        "--config",
                        "experiments/ecdlp_lab/fixtures/smoke.json",
                        "--output",
                        str(output),
                    ]
                )
            self.assertEqual(status, 1)
            self.assertEqual(
                diagnostics.getvalue(),
                "orchestration.config.load: fixture drifted\n",
            )

    def test_coordinator_and_workers_import_no_engine_analysis_or_submission_layer(self) -> None:
        checked = (
            "events.py",
            "method_worker.py",
            "validator_worker.py",
            "runner.py",
            "run_smoke.py",
        )
        forbidden = (
            "experiments.engine",
            "experiments.ecdlp_lab.analysis",
            "repo.research_engine",
        )
        for filename in checked:
            with self.subTest(filename=filename):
                imports = imported_modules(ORCHESTRATION / filename)
                self.assertFalse(
                    {
                        module
                        for module in imports
                        if any(module == name or module.startswith(name + ".") for name in forbidden)
                    }
                )


if __name__ == "__main__":
    unittest.main()
