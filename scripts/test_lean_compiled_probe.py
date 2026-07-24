#!/usr/bin/env python3
"""Regression fixtures for the compiled Lean portability probe."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from lean_compiled_probe import (  # noqa: E402
    PortabilityError,
    classify_axioms,
    compiled_artifact_manifest,
    module_closure,
    parse_probe_output,
    render_probe,
    sanitized_probe_environment,
    select_targets,
)
from lean_portability import canonical_json_bytes, sha256_bytes  # noqa: E402


class LeanCompiledProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.snapshot = {
            "modules": [
                {
                    "module": "Demo",
                    "file": "Demo.lean",
                    "internal_imports": ["Demo.Basic"],
                },
                {
                    "module": "Demo.Basic",
                    "file": "Demo/Basic.lean",
                    "internal_imports": [],
                },
                {
                    "module": "Unused",
                    "file": "Unused.lean",
                    "internal_imports": [],
                },
            ],
            "declarations": [
                {
                    "qualified_name": "Demo.root",
                    "kind": "theorem",
                    "visibility": "public",
                    "file": "Demo.lean",
                },
                {
                    "qualified_name": "Demo.Basic.value",
                    "kind": "def",
                    "visibility": "public",
                    "file": "Demo/Basic.lean",
                },
                {
                    "qualified_name": "Demo.Basic.hidden",
                    "kind": "theorem",
                    "visibility": "private",
                    "file": "Demo/Basic.lean",
                },
                {
                    "qualified_name": "Unused.value",
                    "kind": "def",
                    "visibility": "public",
                    "file": "Unused.lean",
                },
            ],
        }

    def test_module_closure_is_entrypoint_bounded(self) -> None:
        self.assertEqual(
            module_closure(self.snapshot["modules"], ["Demo"]),
            {"Demo", "Demo.Basic"},
        )

    def test_missing_entrypoint_is_rejected(self) -> None:
        with self.assertRaisesRegex(PortabilityError, "entrypoints are absent"):
            module_closure(self.snapshot["modules"], ["Missing"])

    def test_target_selection_excludes_private_and_unimported(self) -> None:
        closure, targets = select_targets(self.snapshot, ["Demo"])
        self.assertEqual(closure, {"Demo", "Demo.Basic"})
        self.assertEqual(
            [item["name"] for item in targets],
            ["Demo.Basic.value", "Demo.root"],
        )

    def test_probe_output_requires_complete_exact_records(self) -> None:
        output = (
            "KEYAI_MODULE\tDemo\n"
            "KEYAI_PROBE\tFOUND\tDemo.root\tDemo\tfalse\tQuot.sound,propext\n"
            "KEYAI_AXIOM\tQuot.sound\taxiom\tInit.Prelude\tfalse\n"
            "KEYAI_AXIOM\tpropext\taxiom\tInit.Classical\tfalse\n"
        )
        records, provenance, modules = parse_probe_output(output, {"Demo"})
        self.assertEqual(records[0]["axioms"], ["Quot.sound", "propext"])
        self.assertEqual(records[0]["visibility"], "public")
        self.assertEqual(provenance["propext"]["kind"], "axiom")
        self.assertEqual(modules, {"Demo"})
        with self.assertRaisesRegex(PortabilityError, "no public constants"):
            parse_probe_output("", {"Demo"})

    def test_axiom_policy_separates_forbidden_and_unexpected(self) -> None:
        records = [
            {
                "name": "Demo.root",
                "status": "found",
                "axioms": ["propext", "sorryAx", "Demo.custom"],
            }
        ]
        result = classify_axioms(
            records,
            ["propext"],
            {
                "propext": {
                    "kind": "axiom",
                    "module": "Init.Core",
                    "private": False,
                }
            },
            ["sorryAx"],
            [
                {
                    "id": "demo-compiler",
                    "trust_class": "compiler",
                    "axioms": ["Demo.custom"],
                }
            ],
            {
                "propext": {
                    "name": "propext",
                    "kind": "axiom",
                    "module": "Init.Core",
                    "private": False,
                },
                "Demo.custom": {
                    "name": "Demo.custom",
                    "kind": "axiom",
                    "module": "Demo",
                    "private": True,
                }
            },
            {"Demo"},
        )
        self.assertEqual(result["allowed"], ["propext"])
        self.assertEqual(result["forbidden"], ["sorryAx"])
        self.assertEqual(
            result["accepted_by_group"][0]["axioms"],
            ["Demo.custom"],
        )
        self.assertEqual(result["unexpected"], [])

    def test_matching_axiom_without_private_provenance_is_rejected(self) -> None:
        records = [
            {
                "name": "Demo.root",
                "status": "found",
                "axioms": ["Demo.native"],
            }
        ]
        result = classify_axioms(
            records,
            [],
            {},
            ["sorryAx"],
            [
                {
                    "id": "demo-compiler",
                    "trust_class": "compiler",
                    "axioms": ["Demo.native"],
                }
            ],
            {
                "Demo.native": {
                    "name": "Demo.native",
                    "kind": "axiom",
                    "module": "Demo",
                    "private": False,
                }
            },
            {"Demo"},
        )
        self.assertEqual(result["unexpected"], ["Demo.native"])
        self.assertEqual(
            result["invalid_accepted_provenance"][0]["reasons"],
            ["not_private"],
        )

    def test_allowed_axiom_requires_exact_provenance(self) -> None:
        records = [
            {
                "name": "Demo.root",
                "status": "found",
                "axioms": ["propext"],
            }
        ]
        result = classify_axioms(
            records,
            ["propext"],
            {
                "propext": {
                    "kind": "axiom",
                    "module": "Init.Core",
                    "private": False,
                }
            },
            [],
            [],
            {
                "propext": {
                    "name": "propext",
                    "kind": "axiom",
                    "module": "Init.Prelude",
                    "private": False,
                }
            },
            {"Demo"},
        )
        self.assertEqual(
            result["invalid_allowed_provenance"],
            [{"axiom": "propext", "reasons": ["unexpected_module"]}],
        )

    def test_rendered_probe_has_only_declarative_imports(self) -> None:
        source = render_probe(["Demo"], ["Demo", "Demo.Basic"])
        self.assertIn("import Demo\n", source)
        self.assertIn("env.constants", source)
        self.assertIn("!isPrivateName name", source)
        self.assertIn("{isPrivateName name}", source)
        self.assertIn('"Demo"', source)
        with self.assertRaisesRegex(PortabilityError, "invalid compiled entrypoint"):
            render_probe(["Demo\n#eval 1"], ["Demo"])

    def test_probe_output_rejects_private_constants(self) -> None:
        output = (
            "KEYAI_MODULE\tDemo\n"
            "KEYAI_PROBE\tFOUND\t_private.Demo.0.secret\tDemo\ttrue\t\n"
        )
        with self.assertRaisesRegex(PortabilityError, "private constant"):
            parse_probe_output(output, {"Demo"})

    def test_sanitized_environment_drops_secret_like_parent_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lake = Path(tmp) / "lake.exe"
            lake.write_bytes(b"test-lake-launcher")
            with patch.dict(
                os.environ,
                {
                    "GITHUB_TOKEN": "must-not-cross-boundary",
                    "SYSTEMROOT": r"C:\Windows",
                },
                clear=False,
            ):
                env, profile = sanitized_probe_environment(
                    str(lake),
                    Path(tmp) / "sandbox",
                    "1",
                )
        self.assertNotIn("GITHUB_TOKEN", env)
        self.assertEqual(profile["secret_like_environment_keys_inherited"], [])
        self.assertEqual(profile["network_isolation"], "not_os_enforced")
        self.assertEqual(
            profile["lake_launcher_sha256"],
            sha256_bytes(b"test-lake-launcher"),
        )
        self.assertEqual(profile["compiled_probe_launcher"], "project_lake_env")
        self.assertEqual(
            profile["compiled_probe_output_authentication"],
            "not_independent_of_project_launcher",
        )

    def test_compiled_artifact_manifest_retains_recomputable_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            artifact = (
                project
                / ".lake"
                / "build"
                / "lib"
                / "lean"
                / "Demo"
                / "Basic.olean"
            )
            artifact.parent.mkdir(parents=True)
            artifact.write_bytes(b"compiled-demo")
            manifest = compiled_artifact_manifest(project, {"Demo.Basic"})
        self.assertEqual(manifest["module_oleans"], 1)
        self.assertEqual(manifest["records"][0]["module"], "Demo.Basic")
        self.assertEqual(
            manifest["records"][0]["path"],
            ".lake/build/lib/lean/Demo/Basic.olean",
        )
        self.assertEqual(
            manifest["manifest_sha256"],
            sha256_bytes(canonical_json_bytes(manifest["records"])),
        )


if __name__ == "__main__":
    unittest.main()
