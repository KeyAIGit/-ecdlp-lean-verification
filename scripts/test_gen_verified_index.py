#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import gen_verified_index


class VerifiedIndexTests(unittest.TestCase):
    def make_root(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / "data").mkdir()

        (root / "data/result_registry.json").write_text(
            json.dumps(
                {
                    "ledger_rows": 2,
                    "ledger_entries": [
                        {
                            "id": "ledger-000",
                            "claim": "field fact",
                            "theorem_cell": "`Ecdlp.fieldFact`",
                            "declared_files": ["Ecdlp/Proved/Field.lean"],
                            "method": "native_decide",
                            "status": "proved",
                            "references": [
                                {
                                    "canonical_name": "Ecdlp.fieldFact",
                                    "kind": "theorem",
                                    "file": "Ecdlp/Proved/Field.lean",
                                    "line": 10,
                                }
                            ],
                        },
                        {
                            "id": "ledger-001",
                            "claim": "generic theorem",
                            "theorem_cell": "`Ecdlp.genericFact`",
                            "declared_files": ["Ecdlp/Proved/Generic.lean"],
                            "method": "Mathlib",
                            "status": "proved",
                            "references": [
                                {
                                    "canonical_name": "Ecdlp.genericFact",
                                    "kind": "theorem",
                                    "file": "Ecdlp/Proved/Generic.lean",
                                    "line": 20,
                                }
                            ],
                        },
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (root / "data/researchos_result_registry.json").write_text(
            json.dumps(
                {
                    "ledger_rows": 1,
                    "ledger_entries": [
                        {
                            "claim_id": "RH-TEST",
                            "domain": "riemann-hypothesis",
                            "declarations": ["ResearchOS.RH.test"],
                            "files": [
                                "ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Test.lean"
                            ],
                            "axiom_base": "standard",
                            "method": "Mathlib",
                            "status": "proved",
                        }
                    ],
                    "declarations": {
                        "ResearchOS.RH.test": {
                            "kind": "theorem",
                            "file": "ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Test.lean",
                            "line": 30,
                        }
                    },
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (root / "data/stats.json").write_text(
            json.dumps({"ledger_rows": 2}, indent=2) + "\n",
            encoding="utf-8",
        )
        return root

    def test_build_preserves_two_lanes_and_trust_levels(self) -> None:
        index = gen_verified_index.build_index(self.make_root())
        self.assertEqual(index["counts"]["navigation_rows_total"], 3)
        self.assertEqual(index["counts"]["ecdlp_rows"], 2)
        self.assertEqual(index["counts"]["researchos_rows"], 1)
        self.assertEqual(index["counts"]["kernel_standard_rows"], 1)
        self.assertEqual(index["counts"]["kernel_audited_rows"], 1)
        self.assertEqual(index["counts"]["kernel_plus_compiler_rows"], 1)
        self.assertEqual({row["lane"] for row in index["results"]}, {"ecdlp", "researchos"})
        self.assertEqual(
            index["counts"]["navigation_rows_total"],
            index["counts"]["kernel_standard_rows"]
            + index["counts"]["kernel_audited_rows"]
            + index["counts"]["kernel_plus_compiler_rows"],
        )

    def test_long_claim_has_stable_short_slug_and_readable_title(self) -> None:
        root = self.make_root()
        registry_path = root / "data/result_registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["ledger_entries"][1]["claim"] = "Long claim " + ("with detailed scope " * 80)
        registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
        index = gen_verified_index.build_index(root)
        row = next(row for row in index["results"] if row["uid"] == "ecdlp/ledger-001")
        self.assertEqual(row["slug"], "ecdlp-ledger-001")
        self.assertLessEqual(len(row["title"]), 180)
        self.assertGreater(len(row["claim_id"]), len(row["title"]))

    def test_rendered_markdown_states_navigation_boundary(self) -> None:
        index = gen_verified_index.build_index(self.make_root())
        rendered = gen_verified_index.render_markdown(index)
        self.assertIn("navigation layer", rendered)
        self.assertIn("not an ECDLP security metric", rendered)
        self.assertIn("Ecdlp.fieldFact", rendered)
        self.assertIn("ResearchOS.RH.test", rendered)

    def test_rejects_cross_lane_file_leak(self) -> None:
        root = self.make_root()
        registry_path = root / "data/result_registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["ledger_entries"][0]["declared_files"] = ["ResearchOS/Leak.lean"]
        registry["ledger_entries"][0]["references"][0]["file"] = "ResearchOS/Leak.lean"
        registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "leaks ResearchOS file"):
            gen_verified_index.build_index(root)

    def test_check_detects_stale_outputs(self) -> None:
        root = self.make_root()
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            self.assertEqual(gen_verified_index.write_or_check(root, check=False), 0)
            self.assertEqual(gen_verified_index.write_or_check(root, check=True), 0)
            (root / "VERIFIED_INDEX.md").write_text("stale\n", encoding="utf-8")
            self.assertEqual(gen_verified_index.write_or_check(root, check=True), 1)
        self.assertIn("verified-index check FAILED", output.getvalue())


if __name__ == "__main__":
    unittest.main()
