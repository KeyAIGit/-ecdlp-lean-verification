#!/usr/bin/env python3
"""Validate the immutable inputs recorded for the bounded ECDLP lab."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
INVENTORY = ROOT / "tasks" / "ECDLP_LAB_REUSE_INVENTORY.json"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
TOP_LEVEL_FIELDS = {
    "baseline",
    "entries",
    "excluded_legacy_surfaces",
    "inventory_id",
    "schema_version",
    "upstream_theta_screen",
}
ENTRY_FIELDS = {
    "id",
    "mutation_policy",
    "owning_validator",
    "path",
    "role",
    "sha256",
}


class InventoryError(ValueError):
    """Raised when the reuse inventory is malformed or drifted."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InventoryError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise InventoryError(f"non-finite JSON constant: {value}")


def load_inventory(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_unique_object,
        parse_constant=_reject_constant,
    )
    if not isinstance(value, dict):
        raise InventoryError("inventory must be a JSON object")
    return value


def repo_path(value: object, context: str, *, must_exist: bool = True) -> Path:
    if not isinstance(value, str) or not value:
        raise InventoryError(f"{context} must be a nonempty repo-relative path")
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or "\\" in value:
        raise InventoryError(f"{context} escapes the repository: {value!r}")
    resolved = (ROOT / Path(*pure.parts)).resolve()
    if resolved != ROOT and ROOT not in resolved.parents:
        raise InventoryError(f"{context} escapes the repository: {value!r}")
    if must_exist and not resolved.is_file():
        raise InventoryError(f"{context} is not a file: {value!r}")
    return resolved


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_tree(path: str) -> str:
    result = subprocess.run(
        ["git", "rev-parse", f"HEAD:{path}"],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        raise InventoryError(f"cannot resolve git tree: {path}")
    return result.stdout.strip()


def validate(value: dict[str, Any]) -> None:
    if set(value) != TOP_LEVEL_FIELDS:
        raise InventoryError("unexpected top-level inventory fields")
    if value["schema_version"] != "1.0":
        raise InventoryError("unsupported schema_version")
    if value["inventory_id"] != "ECDLP-LAB-REUSE-INVENTORY-V1":
        raise InventoryError("unexpected inventory_id")

    baseline = value["baseline"]
    if not isinstance(baseline, dict) or not HEX40.fullmatch(
        str(baseline.get("main_commit", ""))
    ):
        raise InventoryError("baseline.main_commit must be a 40-hex commit")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", baseline["main_commit"], "HEAD"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if ancestor.returncode != 0:
        raise InventoryError("baseline.main_commit is not an ancestor of HEAD")

    entries = value["entries"]
    if not isinstance(entries, list) or not entries:
        raise InventoryError("entries must be a nonempty list")
    ids: set[str] = set()
    paths: set[str] = set()
    for index, entry in enumerate(entries):
        context = f"entries[{index}]"
        if not isinstance(entry, dict) or set(entry) != ENTRY_FIELDS:
            raise InventoryError(f"{context} has unexpected fields")
        if not isinstance(entry["id"], str) or entry["id"] in ids:
            raise InventoryError(f"{context}.id is invalid or duplicated")
        if entry["path"] in paths:
            raise InventoryError(f"{context}.path is duplicated")
        ids.add(entry["id"])
        paths.add(entry["path"])
        path = repo_path(entry["path"], f"{context}.path")
        expected = entry["sha256"]
        if not isinstance(expected, str) or not HEX64.fullmatch(expected):
            raise InventoryError(f"{context}.sha256 must be lowercase 64-hex")
        actual = sha256_file(path)
        if actual != expected:
            raise InventoryError(
                f"{context}.sha256 drifted: expected {expected}, found {actual}"
            )
        policy = entry["mutation_policy"]
        if not isinstance(policy, str) or not policy.startswith("hash_frozen"):
            raise InventoryError(f"{context}.mutation_policy is not frozen")
        if not isinstance(entry["role"], str) or not entry["role"]:
            raise InventoryError(f"{context}.role must be nonempty")
        validator = entry["owning_validator"]
        if validator is not None:
            repo_path(validator, f"{context}.owning_validator")

    excluded = value["excluded_legacy_surfaces"]
    if not isinstance(excluded, list) or not excluded:
        raise InventoryError("excluded_legacy_surfaces must be nonempty")
    for index, surface in enumerate(excluded):
        if not isinstance(surface, dict):
            raise InventoryError(f"excluded_legacy_surfaces[{index}] must be an object")
        if surface.get("digest_algorithm") == "git_tree_sha1":
            expected = surface.get("digest_value")
            if not isinstance(expected, str) or not HEX40.fullmatch(expected):
                raise InventoryError(f"excluded surface {index} has invalid tree digest")
            actual = git_tree(str(surface.get("path", "")))
            if actual != expected:
                raise InventoryError(
                    f"excluded surface {index} drifted: expected {expected}, found {actual}"
                )

    upstream = value["upstream_theta_screen"]
    if not isinstance(upstream, dict):
        raise InventoryError("upstream_theta_screen must be an object")
    for field in ("base_commit", "head_commit"):
        if not HEX40.fullmatch(str(upstream.get(field, ""))):
            raise InventoryError(f"upstream_theta_screen.{field} must be 40-hex")
    if upstream.get("disposition") != "upstream_pending":
        raise InventoryError("upstream disposition must remain upstream_pending")
    if upstream.get("merge_authorized") is not False:
        raise InventoryError("unreplayed upstream may not be merge-authorized")
    files = upstream.get("files")
    if not isinstance(files, list) or not files:
        raise InventoryError("upstream files must be recorded")
    for index, item in enumerate(files):
        if (
            not isinstance(item, dict)
            or set(item) != {"path", "sha256"}
            or not HEX64.fullmatch(str(item.get("sha256", "")))
        ):
            raise InventoryError(f"upstream files[{index}] is malformed")
        repo_path(item["path"], f"upstream files[{index}].path", must_exist=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", type=Path, default=INVENTORY)
    args = parser.parse_args()
    inventory = args.inventory
    if not inventory.is_absolute():
        inventory = ROOT / inventory
    try:
        value = load_inventory(inventory)
        validate(value)
    except (InventoryError, OSError, json.JSONDecodeError) as exc:
        print(f"ECDLP lab reuse inventory FAILED: {exc}")
        return 1
    print(
        "ECDLP lab reuse inventory OK: "
        f"{len(value['entries'])} frozen files, "
        f"{len(value['excluded_legacy_surfaces'])} excluded surfaces, "
        "theta upstream pending"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
