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
import shutil
import subprocess
import sys
from pathlib import PurePosixPath
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


def parse_manifest(text: str) -> tuple[dict[str, ArtifactClass], list[str], list[str]]:
    classes: dict[str, ArtifactClass] = {}
    cleanup_paths: list[str] = []
    allowed_overlaps: list[str] = []

    in_classes = False
    current_class: ArtifactClass | None = None
    current_list: str | None = None
    top_list: str | None = None

    for line in text.splitlines():
        if line.startswith("classes:"):
            in_classes = True
            current_class = None
            current_list = None
            continue

        if line.startswith("allowed_overlap_paths:"):
            top_list = "allowed_overlap_paths"
            continue
        if line.startswith("cleanup_candidates:"):
            top_list = "cleanup_candidates"
            continue
        if line and not line.startswith(" "):
            top_list = None

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

        overlap_match = re.match(r"^  - (.+)$", line)
        if overlap_match and top_list == "allowed_overlap_paths":
            allowed_overlaps.append(normalize_item(overlap_match.group(1)))

        cleanup_match = re.match(r"^  - path: (.+)$", line)
        if cleanup_match and top_list == "cleanup_candidates":
            cleanup_paths.append(normalize_item(cleanup_match.group(1)))

    return classes, cleanup_paths, allowed_overlaps


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


def pattern_matches_file(pattern: str, path: str) -> bool:
    if pattern.endswith("/"):
        return path.startswith(pattern)
    if any(ch in pattern for ch in "*?[]"):
        return PurePosixPath(path).match(pattern)
    return path == pattern


def repository_files() -> list[str]:
    git = shutil.which("git")
    if not git:
        runtime_root = Path.home() / ".cache" / "codex-runtimes"
        git = next((str(path) for path in runtime_root.rglob("git.exe")), None)
    if not git:
        raise RuntimeError("git executable not found; cannot classify tracked files")
    command = [
        git, "ls-files", "--cached", "--others", "--exclude-standard",
    ]
    result = subprocess.run(
        command, cwd=ROOT, check=True, text=True, capture_output=True, encoding="utf-8"
    )
    return sorted(line for line in result.stdout.splitlines() if line)


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

    classes, cleanup_paths, allowed_overlaps = parse_manifest(
        MANIFEST.read_text(encoding="utf-8")
    )

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

    files = repository_files()
    classifications: dict[str, list[str]] = {}
    for path in files:
        classifications[path] = [
            class_name
            for class_name, artifact_class in classes.items()
            if any(pattern_matches_file(pattern, path) for pattern in artifact_class.paths)
        ]
    unclassified = [path for path, owners in classifications.items() if not owners]
    overlaps = {
        path: owners for path, owners in classifications.items()
        if len(owners) > 1 and path not in allowed_overlaps
    }
    for path in unclassified:
        errors.append(f"unclassified tracked file: {path}")
    for path, owners in overlaps.items():
        errors.append(f"unapproved class overlap: {path} -> {', '.join(owners)}")
    for path in allowed_overlaps:
        if path not in classifications:
            errors.append(f"allowed overlap path is not tracked: {path}")
        elif len(classifications[path]) < 2:
            errors.append(f"allowed overlap path no longer overlaps classes: {path}")

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
        ["repo/FORMAL_SUBSTRATE.json", "repo/ARTIFACTS.yaml"],
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
        f"{len(files)} repository files exhaustively classified, "
        f"{checked_paths} path entries"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
