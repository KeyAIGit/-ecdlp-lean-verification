from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from experiments.ecdlp_lab.orchestration.allowlist import (
    METHOD_ALLOWLIST_PATH,
    allowed_method_ids,
    load_method_allowlist,
    resolve_method,
)
from experiments.ecdlp_lab.orchestration.model import OrchestrationError


REPO_ROOT = Path(__file__).resolve().parents[3]


class P04AllowlistTests(unittest.TestCase):
    def test_allowlist_contains_only_the_two_frozen_data_only_methods(self) -> None:
        descriptors = load_method_allowlist(repo_root=REPO_ROOT)
        self.assertEqual(
            tuple(descriptor.method_id for descriptor in descriptors),
            ("bsgs_v1", "ordinary_rho_xmod3_v1"),
        )
        self.assertEqual(
            allowed_method_ids(repo_root=REPO_ROOT),
            frozenset({"bsgs_v1", "ordinary_rho_xmod3_v1"}),
        )
        for descriptor in descriptors:
            self.assertEqual(set(vars(descriptor)), {"method_id"})
            self.assertEqual(set(descriptor.as_dict()), {"method_id"})
            for forbidden in ("command", "path", "argv", "module", "executable"):
                self.assertFalse(hasattr(descriptor, forbidden))

    def test_resolution_is_exact_and_never_interprets_executable_text(self) -> None:
        self.assertEqual(
            resolve_method("bsgs_v1", repo_root=REPO_ROOT).method_id, "bsgs_v1"
        )
        for value in (
            "BSGS_v1",
            "bsgs_v1 ",
            "../../bsgs_v1",
            "bsgs_v1;python",
            "unknown_v1",
            None,
        ):
            with self.subTest(value=value):
                with self.assertRaises(OrchestrationError):
                    resolve_method(value, repo_root=REPO_ROOT)  # type: ignore[arg-type]

    def test_allowlist_raw_bytes_are_pinned(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = REPO_ROOT.joinpath(*METHOD_ALLOWLIST_PATH.split("/"))
            destination = root.joinpath(*METHOD_ALLOWLIST_PATH.split("/"))
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            destination.write_bytes(destination.read_bytes() + b"\n")
            with self.assertRaisesRegex(OrchestrationError, "raw allowlist bytes drifted"):
                load_method_allowlist(repo_root=root)


if __name__ == "__main__":
    unittest.main()
