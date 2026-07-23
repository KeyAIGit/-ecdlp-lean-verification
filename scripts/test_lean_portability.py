#!/usr/bin/env python3
"""Regression fixtures for the read-only Lean portability snapshot."""
from __future__ import annotations

import copy
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from lean_portability import (  # noqa: E402
    PortabilityError,
    build_snapshot,
    canonical_json_bytes,
    git_environment,
    module_for_path,
    normalized_source_sha256,
    parse_declarations,
    parse_imports,
    resolve_output,
    sha256_bytes,
    strip_comments_and_strings,
    validate_adapter,
)


class LeanPortabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="keyai-portability-test-")
        self.root = Path(self.tmp.name)
        (self.root / "Demo").mkdir()
        (self.root / ".github" / "workflows").mkdir(parents=True)
        self.files = {
            "Demo.lean": (
                "import Demo.Basic Mathlib\n"
                "namespace Demo\n"
                "theorem root : True := by trivial\n"
                "end Demo\n"
            ),
            "Demo/Basic.lean": (
                "namespace Demo\n"
                "section\n"
                "/- nested /- sorry -/ comment -/\n"
                "lemma kept : True := by trivial\n"
                'def message := "sorry axiom fake"\n'
                "private theorem hidden : True := by trivial\n"
                "instance : Inhabited Unit := inferInstance\n"
                "end\n"
                "axiom declaredBoundary : Prop\n"
                "end Demo\n"
            ),
            "Scratch.lean": "theorem outside : True := by trivial\n",
            "lakefile.toml": 'name = "demo"\n',
            "lean-toolchain": "leanprover/lean4:v4.19.0\n",
            "LICENSE": "Apache License\n",
            "README.md": "# Demo\n",
            ".github/workflows/ci.yml": "name: CI\n",
            "notes.json": "{}\n",
        }
        for rel, text in self.files.items():
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
        self.contract = {
            "selected_source": {
                "repository": "https://github.com/example/demo",
                "commit_sha": "a" * 40,
                "tree_sha": "b" * 40,
                "license_spdx": "Apache-2.0",
                "license_file": "LICENSE",
                "license_sha256": sha256_bytes(self.files["LICENSE"].encode("utf-8")),
                "toolchain_file": "lean-toolchain",
                "lean_toolchain": "leanprover/lean4:v4.19.0",
                "adapter": {
                    "module_roots": [{"path": "Demo", "module_prefix": "Demo"}],
                    "entrypoints": ["Demo.Basic"],
                    "owned_module_prefixes": ["Demo"],
                    "explicit_exclusions": [],
                },
            },
            "id": "KEYAI-PORTABILITY-TEST",
            "task_id": "TASK-TEST",
            "artifacts": {
                "snapshot": "rehearsals/keyai-portability-test/snapshot.json"
            },
        }

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def snapshot(self) -> dict:
        return build_snapshot(
            self.root,
            self.contract,
            "a" * 40,
            sorted(self.files),
        )

    def test_snapshot_is_deterministic_and_complete(self) -> None:
        first = self.snapshot()
        second = self.snapshot()
        self.assertEqual(canonical_json_bytes(first), canonical_json_bytes(second))
        self.assertEqual(first["summary"]["tracked_files"], len(self.files))
        self.assertEqual(first["summary"]["classified_files"], len(self.files))
        self.assertEqual(first["summary"]["lean_modules"], 1)
        self.assertEqual(first["summary"]["unsupported_lean_files"], 2)
        self.assertFalse(first["external_evidence"])
        self.assertFalse(first["unlocks_task_012"])

    def test_comments_and_strings_do_not_create_false_trust_tokens(self) -> None:
        snapshot = self.snapshot()
        self.assertEqual(snapshot["summary"]["sorry_tokens"], 0)
        self.assertEqual(snapshot["summary"]["admit_tokens"], 0)
        self.assertEqual(
            snapshot["axiom_or_constant_declarations"],
            ["Demo.declaredBoundary"],
        )

    def test_declarations_preserve_visibility_and_anonymous_instances(self) -> None:
        snapshot = self.snapshot()
        by_name = {
            item["qualified_name"]: item for item in snapshot["declarations"]
        }
        self.assertIn("Demo.kept", by_name)
        self.assertEqual(by_name["Demo.hidden"]["visibility"], "private")
        self.assertEqual(snapshot["summary"]["anonymous_instances"], 1)

    def test_imports_split_multiple_modules(self) -> None:
        adapter = copy.deepcopy(self.contract["selected_source"]["adapter"])
        adapter["module_roots"].append({"path": ".", "module_prefix": ""})
        adapter["entrypoints"] = ["Demo"]
        self.contract["selected_source"]["adapter"] = adapter
        snapshot = self.snapshot()
        root = next(item for item in snapshot["modules"] if item["module"] == "Demo")
        self.assertEqual(root["imports"], ["Demo.Basic", "Mathlib"])
        self.assertEqual(root["internal_imports"], ["Demo.Basic"])
        self.assertEqual(root["external_imports"], ["Mathlib"])

    def test_module_mapping_uses_most_specific_root(self) -> None:
        roots = [
            {"path": ".", "module_prefix": ""},
            {"path": "Demo", "module_prefix": "Portable"},
        ]
        self.assertEqual(
            module_for_path("Demo/Basic.lean", roots),
            "Portable.Basic",
        )

    def test_nested_comments_preserve_newlines(self) -> None:
        original = "theorem a : True := by\n/- x\n/- y -/\n-/\ntrivial\n"
        clean = strip_comments_and_strings(original)
        self.assertEqual(clean.count("\n"), original.count("\n"))
        self.assertNotIn("/- y -/", clean)
        self.assertIn("trivial", clean)

    def test_module_syntax_public_imports_and_mutual_blocks(self) -> None:
        source = (
            "module\n"
            "public import Demo.Dependency\n"
            "namespace Demo\n"
            "mutual\n"
            "public def first : Nat := second\n"
            "def second : Nat := 1\n"
            "end\n"
            "public theorem kept : first = 1 := rfl\n"
            "end Demo\n"
        )
        self.assertEqual(parse_imports(source), ["Demo.Dependency"])
        declarations, _ = parse_declarations(source, "Demo.lean")
        by_name = {item["qualified_name"]: item for item in declarations}
        self.assertIn("Demo.kept", by_name)
        self.assertEqual(by_name["Demo.first"]["visibility"], "public")
        self.assertEqual(
            by_name["Demo.second"]["visibility"],
            "module_private",
        )

    def test_attributed_public_section_controls_visibility(self) -> None:
        source = (
            "module\n"
            "namespace Demo\n"
            "@[expose] public section\n"
            "def exported : Nat := 1\n"
            "private def hidden : Nat := 2\n"
            "end\n"
            "def moduleOnly : Nat := 3\n"
            "end Demo\n"
        )
        declarations, _ = parse_declarations(source, "Demo.lean")
        by_name = {item["qualified_name"]: item for item in declarations}
        self.assertEqual(by_name["Demo.exported"]["visibility"], "public")
        self.assertEqual(by_name["Demo.hidden"]["visibility"], "private")
        self.assertEqual(
            by_name["Demo.moduleOnly"]["visibility"],
            "module_private",
        )

    def test_duplicate_module_root_is_rejected(self) -> None:
        adapter = copy.deepcopy(self.contract["selected_source"]["adapter"])
        adapter["module_roots"].append(
            {"path": "Demo", "module_prefix": "Other"}
        )
        with self.assertRaisesRegex(PortabilityError, "unique paths"):
            validate_adapter(adapter)

    def test_unsafe_module_root_is_rejected(self) -> None:
        adapter = copy.deepcopy(self.contract["selected_source"]["adapter"])
        adapter["module_roots"] = [{"path": "../escape", "module_prefix": ""}]
        with self.assertRaises(PortabilityError):
            validate_adapter(adapter)

    def test_git_environment_drops_secret_like_parent_keys(self) -> None:
        with patch.dict(
            os.environ,
            {
                "GITHUB_TOKEN": "must-not-cross-boundary",
                "SYSTEMROOT": r"C:\Windows",
            },
            clear=False,
        ):
            env = git_environment()
        self.assertNotIn("GITHUB_TOKEN", env)
        self.assertEqual(env["GIT_OPTIONAL_LOCKS"], "0")
        self.assertEqual(env["GIT_TERMINAL_PROMPT"], "0")
        self.assertEqual(
            env["GIT_CONFIG_GLOBAL"],
            "NUL" if os.name == "nt" else "/dev/null",
        )

    def test_normalized_source_hash_is_line_ending_independent(self) -> None:
        lf = self.root / "lf.py"
        crlf = self.root / "crlf.py"
        lf.write_bytes(b"first\nsecond\n")
        crlf.write_bytes(b"first\r\nsecond\r\n")
        self.assertEqual(
            normalized_source_sha256(lf),
            normalized_source_sha256(crlf),
        )

    def test_snapshot_digest_self_check(self) -> None:
        snapshot = self.snapshot()
        digest = snapshot.pop("snapshot_sha256")
        self.assertEqual(digest, sha256_bytes(canonical_json_bytes(snapshot)))

    def test_license_hash_mismatch_is_rejected(self) -> None:
        self.contract["selected_source"]["license_sha256"] = "0" * 64
        with self.assertRaisesRegex(PortabilityError, "license hash mismatch"):
            self.snapshot()

    def test_missing_entrypoint_is_rejected(self) -> None:
        self.contract["selected_source"]["adapter"]["entrypoints"] = ["Demo.Missing"]
        with self.assertRaisesRegex(PortabilityError, "entrypoints are missing"):
            self.snapshot()

    def test_unresolved_owned_import_is_rejected(self) -> None:
        rel = "Demo/Basic.lean"
        self.files[rel] = "import Demo.Missing\n" + self.files[rel]
        (self.root / rel).write_text(
            self.files[rel],
            encoding="utf-8",
            newline="\n",
        )
        with self.assertRaisesRegex(PortabilityError, "unresolved local imports"):
            self.snapshot()

    def test_module_collision_is_rejected(self) -> None:
        rel = "Other/Basic.lean"
        self.files[rel] = "theorem other : True := by trivial\n"
        (self.root / rel).parent.mkdir()
        (self.root / rel).write_text(
            self.files[rel],
            encoding="utf-8",
            newline="\n",
        )
        adapter = self.contract["selected_source"]["adapter"]
        adapter["module_roots"].append(
            {"path": "Other", "module_prefix": "Demo"}
        )
        with self.assertRaisesRegex(PortabilityError, "module collision"):
            self.snapshot()

    def test_snapshot_output_is_rehearsal_owned(self) -> None:
        output = resolve_output(self.contract)
        self.assertEqual(
            output.relative_to(ROOT).as_posix(),
            "rehearsals/keyai-portability-test/snapshot.json",
        )
        self.contract["artifacts"]["snapshot"] = "README.md"
        with self.assertRaisesRegex(PortabilityError, "must be exactly"):
            resolve_output(self.contract)

    def test_symlink_object_is_visible_and_not_parsed_as_lean(self) -> None:
        rel = "Demo/Linked.lean"
        self.files[rel] = "../outside.lean"
        (self.root / rel).write_text(self.files[rel], encoding="utf-8")
        entries = {
            path: {
                "mode": "120000" if path == rel else "100644",
                "object_type": "blob",
                "object_id": "b" * 40,
            }
            for path in self.files
        }
        snapshot = build_snapshot(
            self.root,
            self.contract,
            "a" * 40,
            sorted(self.files),
            git_entries=entries,
        )
        record = next(item for item in snapshot["files"] if item["path"] == rel)
        self.assertEqual(record["classification"], "symlink")
        self.assertIn(rel, snapshot["unsupported_lean_files"])


if __name__ == "__main__":
    unittest.main()
