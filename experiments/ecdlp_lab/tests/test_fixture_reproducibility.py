from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from experiments.ecdlp_lab.core.canonical_json import sha256_hex


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


class FixtureReproducibilityTests(unittest.TestCase):
    def test_fixture_manifest_matches(self) -> None:
        manifest = json.loads((FIXTURES / "manifest.json").read_text())
        for name, expected in manifest["files"].items():
            value = json.loads((FIXTURES / name).read_text())
            self.assertEqual(expected, sha256_hex(value), name)

    def test_generator_is_deterministic(self) -> None:
        tracked = [
            "registry.json",
            "valid_records.json",
            "invalid_records.json",
            "invalid_raw_json.json",
            "manifest.json",
        ]
        before = {name: hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest() for name in tracked}
        subprocess.run(
            [sys.executable, str(FIXTURES / "build_fixtures.py")],
            check=True,
            cwd=Path(__file__).resolve().parents[3],
            stdout=subprocess.DEVNULL,
        )
        after = {name: hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest() for name in tracked}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
