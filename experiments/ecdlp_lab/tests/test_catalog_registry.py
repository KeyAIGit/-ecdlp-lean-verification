from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from experiments.ecdlp_lab.core.catalog_registry import (
    CI_CATALOG_ID,
    LEGACY_CATALOG_ID,
    REGISTRY_KIND,
    REGISTRY_PATH,
    CatalogRegistryError,
    load_catalog_registry,
    resolve_catalog,
    trusted_catalog_sha256s,
)


CI_PATH = "experiments/ecdlp_lab/fixtures/curves/ci_curve_catalog_v1.json"
SPEC_PATH = "experiments/ecdlp_lab/fixtures/curves/ci_catalog_spec_v1.json"
LEGACY_PATH = "experiments/ml_structure_probe/reports/p1_toy_scaling/curve_catalog.json"


def raw_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def write(root: Path, relative: str, payload: bytes) -> Path:
    path = root.joinpath(*relative.split("/"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return path


def fixture_catalog(spec_sha256: str) -> dict[str, object]:
    return {
        "schema_version": 1,
        "catalog_kind": CI_CATALOG_ID,
        "classification": "engineering_only",
        "native_research_outcome": False,
        "spec_sha256": spec_sha256,
        "curve_count": 6,
        "field_bits": [11, 13],
        "families": [
            "j0_glv_like",
            "j0_no_fp_glv_control",
            "random_generic_j_prime_subgroup",
        ],
        "limits": {
            "max_prime_candidates": 4096,
            "max_curve_candidates": 4096,
            "max_point_attempts": 1024,
        },
        "fixtures": [{"fixture_id": f"fixture_{index}"} for index in range(6)],
    }


def build_repository(root: Path) -> dict[str, object]:
    spec_bytes = raw_json({"schema_version": 1, "spec_kind": "test_spec_v1"})
    spec_sha256 = digest(spec_bytes)
    catalog_bytes = raw_json(fixture_catalog(spec_sha256))
    legacy_bytes = b'{"legacy":true,"wall_time_seconds":0.25}\n'
    write(root, SPEC_PATH, spec_bytes)
    write(root, CI_PATH, catalog_bytes)
    write(root, LEGACY_PATH, legacy_bytes)
    registry = {
        "schema_version": 1,
        "registry_kind": REGISTRY_KIND,
        "catalogs": [
            {
                "catalog_id": CI_CATALOG_ID,
                "source_kind": "committed_lab_catalog",
                "path": CI_PATH,
                "sha256": digest(catalog_bytes),
                "curve_count": 6,
                "spec_path": SPEC_PATH,
                "spec_sha256": spec_sha256,
            },
            {
                "catalog_id": LEGACY_CATALOG_ID,
                "source_kind": "read_only_legacy_catalog",
                "path": LEGACY_PATH,
                "sha256": digest(legacy_bytes),
                "curve_count": 40,
                "spec_path": None,
                "spec_sha256": None,
            },
        ],
    }
    write(root, REGISTRY_PATH, raw_json(registry))
    return registry


class CatalogRegistryTests(unittest.TestCase):
    def test_registry_is_the_complete_catalog_authority(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = build_repository(root)
            expected = frozenset(row["sha256"] for row in registry["catalogs"])
            authorities = load_catalog_registry(repo_root=root)
            self.assertEqual(
                [authority.catalog_id for authority in authorities],
                [CI_CATALOG_ID, LEGACY_CATALOG_ID],
            )
            self.assertEqual(trusted_catalog_sha256s(repo_root=root), expected)
            ci_digest = registry["catalogs"][0]["sha256"]
            self.assertEqual(
                resolve_catalog(ci_digest, repo_root=root).catalog_id, CI_CATALOG_ID
            )
            with self.assertRaises(CatalogRegistryError):
                resolve_catalog("f" * 64, repo_root=root)

    def test_any_catalog_or_spec_drift_fails_the_whole_registry(self) -> None:
        cases = (
            (CI_PATH, b"\n"),
            (SPEC_PATH, b"\n"),
            (LEGACY_PATH, b"\n"),
        )
        for relative_path, suffix in cases:
            with self.subTest(relative_path=relative_path):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    build_repository(root)
                    path = root.joinpath(*relative_path.split("/"))
                    path.write_bytes(path.read_bytes() + suffix)
                    with self.assertRaises(CatalogRegistryError):
                        trusted_catalog_sha256s(repo_root=root)

    def test_catalog_must_bind_the_registry_authorized_spec(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = build_repository(root)
            catalog = fixture_catalog("f" * 64)
            catalog_bytes = raw_json(catalog)
            write(root, CI_PATH, catalog_bytes)
            registry["catalogs"][0]["sha256"] = digest(catalog_bytes)
            write(root, REGISTRY_PATH, raw_json(registry))
            with self.assertRaisesRegex(CatalogRegistryError, "does not bind"):
                load_catalog_registry(repo_root=root)

    def test_registry_and_entry_shapes_are_closed(self) -> None:
        mutations = (
            lambda registry: registry.update({"unknown": True}),
            lambda registry: registry["catalogs"][0].update({"unknown": True}),
            lambda registry: registry["catalogs"].reverse(),
            lambda registry: registry["catalogs"][0].update({"curve_count": True}),
            lambda registry: registry["catalogs"][1].update(
                {"spec_path": SPEC_PATH, "spec_sha256": "f" * 64}
            ),
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    registry = build_repository(root)
                    mutation(registry)
                    write(root, REGISTRY_PATH, raw_json(registry))
                    with self.assertRaises(CatalogRegistryError):
                        load_catalog_registry(repo_root=root)

    def test_unsafe_catalog_paths_are_rejected(self) -> None:
        unsafe_paths = ("../catalog.json", "/tmp/catalog.json", r"bad\catalog.json")
        for unsafe_path in unsafe_paths:
            with self.subTest(unsafe_path=unsafe_path):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    registry = build_repository(root)
                    registry["catalogs"][0]["path"] = unsafe_path
                    write(root, REGISTRY_PATH, raw_json(registry))
                    with self.assertRaises(CatalogRegistryError):
                        load_catalog_registry(repo_root=root)

    def test_symlinked_catalog_spec_and_registry_are_rejected(self) -> None:
        for relative_path in (CI_PATH, SPEC_PATH, REGISTRY_PATH):
            with self.subTest(relative_path=relative_path):
                with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
                    root = Path(directory)
                    build_repository(root)
                    path = root.joinpath(*relative_path.split("/"))
                    payload = path.read_bytes()
                    path.unlink()
                    outside_path = Path(outside) / "payload"
                    outside_path.write_bytes(payload)
                    try:
                        path.symlink_to(outside_path)
                    except (NotImplementedError, OSError) as error:
                        self.skipTest(f"symlinks unavailable: {error}")
                    with self.assertRaises(CatalogRegistryError):
                        load_catalog_registry(repo_root=root)


if __name__ == "__main__":
    unittest.main()
