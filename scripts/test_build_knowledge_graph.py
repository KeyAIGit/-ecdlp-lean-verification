#!/usr/bin/env python3
"""Cross-platform determinism fixtures for the knowledge-graph generator."""

from __future__ import annotations

import unittest
from pathlib import PurePosixPath, PureWindowsPath

from build_knowledge_graph import stable_repo_path


class KnowledgeGraphDeterminismTests(unittest.TestCase):
    def test_module_order_is_identical_across_path_flavors(self) -> None:
        relative = [
            "Ecdlp/Proved/Secp256k1Params.lean",
            "Ecdlp/Proved/Secp256k1PMinusOneSmoothness.lean",
            "Ecdlp/Proved/Secp256k1PrimeP.lean",
        ]
        windows_root = PureWindowsPath("C:/repo")
        posix_root = PurePosixPath("/repo")
        windows = [windows_root / item for item in relative]
        posix = [posix_root / item for item in relative]

        windows_order = [
            stable_repo_path(path, windows_root)
            for path in sorted(
                windows,
                key=lambda path: stable_repo_path(path, windows_root),
            )
        ]
        posix_order = [
            stable_repo_path(path, posix_root)
            for path in sorted(
                posix,
                key=lambda path: stable_repo_path(path, posix_root),
            )
        ]

        self.assertEqual(posix_order, windows_order)
        self.assertEqual(
            [
                "Ecdlp/Proved/Secp256k1PMinusOneSmoothness.lean",
                "Ecdlp/Proved/Secp256k1Params.lean",
                "Ecdlp/Proved/Secp256k1PrimeP.lean",
            ],
            windows_order,
        )


if __name__ == "__main__":
    unittest.main()
