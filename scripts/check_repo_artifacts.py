#!/usr/bin/env python3
"""Validate the repository artifact manifest.

This is intentionally dependency-free. `repo/ARTIFACTS.yaml` is a review
manifest, not a runtime configuration file, so this checker parses only the
small subset of YAML shape the manifest uses:

- `classes.<name>.paths`
- `classes.<name>.generators`
- top-level `cleanup_candidates[].path`

The goal is to keep the architecture map honest: no broken paths, no empty
globs, no missing generators, and no hidden architecture docs that agents never
see from the normal entry points.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "repo" / "ARTIFACTS.yaml"


@dataclass
class ArtifactClass:
    name: str
    paths: list[str] = field(default_factory=list)
    generators: list[str] = field(default_factory=list)


def normalize_item(raw: str) -> str:
    """Strip simple YAML quoting and comments for manifest list values."""
    value = raw.strip()
    if " #" in value:
        value = value.split(" #", 1)[0].rstrip()
    if (value.startswith("'") and value.endswith("'")) or (
        value.startswith('"') and value.endswith('"')
    ):
        value = value[1:-1]
    return value


def parse_manifest(text: str) -> tuple[dict[str, ArtifactClass], list[str]]:
    classes: dict[str, ArtifactClass] = {}
    cleanup_paths: list[str] = []

    in_classes = False
    current_class: ArtifactClass | None = None
    current_list: str | None = None

    for line in text.splitlines():
        if line.startswith("classes:"):
            in_classes = True
            current_class = None
            current_list = None
            continue

        if line and not line.startswith(" ") and not line.startswith("-"):
            in_classes = False
            current_class = None
            current_list = None

        if in_classes:
            class_match = re.match(r"^  ([a-z0-9_]+):\s*$", line)
            if class_match:
                name = class_match.group(1)
                current_class = classes.setdefault(name, ArtifactClass(name=name))
                current_list = None
                continue

            key_match = re.match(r"^    ([a-z_]+):\s*$", line)
            if key_match and current_class:
                key = key_match.group(1)
                current_list = key if key in {"paths", "generators"} else None
                continue

            item_match = re.match(r"^      - (.+)$", line)
            if item_match and current_class and current_list:
                item = normalize_item(item_match.group(1))
                getattr(current_class, current_list).append(item)
                continue

        cleanup_match = re.match(r"^  - path: (.+)$", line)
        if cleanup_match:
            cleanup_paths.append(normalize_item(cleanup_match.group(1)))

    return classes, cleanup_paths


def is_safe_relative_path(pattern: str) -> bool:
    path = Path(pattern)
    return (
        not path.is_absolute()
        and ":" not in pattern
        and "\\" not in pattern
        and ".." not in path.parts
        and pattern.strip() == pattern
        and bool(pattern)
    )


def matches(pattern: str) -> list[Path]:
    if any(ch in pattern for ch in "*?[]"):
        return sorted(ROOT.glob(pattern))
    candidate = ROOT / pattern.rstrip("/")
    return [candidate] if candidate.exists() else []


def require_contains(path: str, needles: list[str], errors: list[str]) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            errors.append(f"{path}: missing required reference {needle!r}")


def main() -> int:
    errors: list[str] = []

    if not MANIFEST.exists():
        print("repo artifact check failed:")
        print("- repo/ARTIFACTS.yaml is missing")
        return 1

    classes, cleanup_paths = parse_manifest(MANIFEST.read_text(encoding="utf-8"))

    if not classes:
        errors.append("repo/ARTIFACTS.yaml: no classes parsed")

    for required in [
        "kernel_verified_surface",
        "generated_views",
        "research_os_control_plane",
        "archive",
    ]:
        if required not in classes:
            errors.append(f"repo/ARTIFACTS.yaml: missing class {required!r}")

    checked_paths = 0
    for class_name, artifact_class in classes.items():
        if not artifact_class.paths:
            errors.append(f"repo/ARTIFACTS.yaml: class {class_name!r} has no paths")

        for pattern in artifact_class.paths:
            checked_paths += 1
            if not is_safe_relative_path(pattern):
                errors.append(f"{class_name}: unsafe path pattern {pattern!r}")
                continue
            found = matches(pattern)
            if not found:
                errors.append(f"{class_name}: path/glob has no matches: {pattern}")

        for generator in artifact_class.generators:
            checked_paths += 1
            if not is_safe_relative_path(generator):
                errors.append(f"{class_name}: unsafe generator path {generator!r}")
                continue
            found = matches(generator)
            if not found:
                errors.append(f"{class_name}: generator does not exist: {generator}")

    # Tranche-1 cleanup was executed (ROADMAP.md §4): candidates moved to archive/,
    # so the manifest may legitimately hold few (or eventually zero) candidates.
    if not cleanup_paths:
        errors.append("repo/ARTIFACTS.yaml: cleanup_candidates section missing or empty "
                      "(keep at least the section with remaining candidates, or an explicit record)")

    for pattern in cleanup_paths:
        checked_paths += 1
        if not is_safe_relative_path(pattern):
            errors.append(f"cleanup_candidates: unsafe path {pattern!r}")
            continue
        if not matches(pattern):
            errors.append(f"cleanup_candidates: path does not exist: {pattern}")

    require_contains(
        "README.md",
        ["REPOSITORY_ARCHITECTURE.md", "repo/ARTIFACTS.yaml"],
        errors,
    )
    require_contains(
        "AGENTS.md",
        ["REPOSITORY_ARCHITECTURE.md", "repo/ARTIFACTS.yaml"],
        errors,
    )
    require_contains(
        "tasks/NEXT.md",
        ["REPOSITORY_ARCHITECTURE.md", "repo/CLEANUP_PLAN.md"],
        errors,
    )
    require_contains(
        "READ_FIRST.md",
        ["REPOSITORY_ARCHITECTURE.md"],
        errors,
    )
    require_contains(
        "CLAUDE.md",
        ["REPOSITORY_ARCHITECTURE.md", "repo/ARTIFACTS.yaml"],
        errors,
    )
    require_contains(
        "archive/ward/README.md",
        ["Repository classification: experimental trace / archive candidate"],
        errors,
    )
    require_contains(
        "archive/scratch/README.md",
        [
            "Repository classification: experimental trace / archive candidate",
            "repo/CLEANUP_PLAN.md",
        ],
        errors,
    )

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if ".github/workflows/stats.yml" in readme:
        errors.append("README.md still points at retired .github/workflows/stats.yml")

    if errors:
        print("repo artifact check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "repo artifact check OK: "
        f"{len(classes)} classes, {len(cleanup_paths)} cleanup candidates, "
        f"{checked_paths} path entries"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
