from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from experiments.ecdlp_lab.core.canonical_json import (
    CanonicalJSONError,
    dumps_canonical,
    loads_strict,
    sha256_hex,
)
from experiments.ecdlp_lab.core.path_policy import PathPolicyError, resolve_within_root


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


class CanonicalJSONTests(unittest.TestCase):
    def test_canonical_order_is_stable(self) -> None:
        left = {"b": [2, 1], "a": {"y": True, "x": None}}
        right = {"a": {"x": None, "y": True}, "b": [2, 1]}
        self.assertEqual(dumps_canonical(left), dumps_canonical(right))
        self.assertEqual(sha256_hex(left), sha256_hex(right))

    def test_invalid_raw_json_fixtures(self) -> None:
        cases = json.loads((FIXTURES / "invalid_raw_json.json").read_text())
        for case in cases:
            with self.subTest(case=case["name"]):
                with self.assertRaisesRegex(CanonicalJSONError, case["expected_error"]):
                    loads_strict(case["text"])

    def test_symlink_escape_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as root_text, tempfile.TemporaryDirectory() as outside_text:
            root = Path(root_text)
            outside = Path(outside_text)
            (outside / "secret.txt").write_text("not inside", encoding="utf-8")
            (root / "link").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(PathPolicyError, "escapes"):
                resolve_within_root(root, "link/secret.txt")


if __name__ == "__main__":
    unittest.main()
