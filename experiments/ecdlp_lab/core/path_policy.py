"""Safe relative path checks for content-addressed lab artifacts."""

from __future__ import annotations

import os
import re
from pathlib import Path, PurePosixPath


class PathPolicyError(ValueError):
    """Raised when a lab path can escape its declared root."""


_DRIVE = re.compile(r"^[A-Za-z]:")


def validate_relative_posix_path(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value:
        raise PathPolicyError("path must be a nonempty string")
    if "\x00" in value:
        raise PathPolicyError("NUL is forbidden in paths")
    if "\\" in value:
        raise PathPolicyError("backslashes and Windows paths are forbidden")
    if value.startswith(("/", "~")) or _DRIVE.match(value):
        raise PathPolicyError("absolute, home-relative, and drive paths are forbidden")
    path = PurePosixPath(value)
    if path.is_absolute():
        raise PathPolicyError("absolute paths are forbidden")
    if any(part in ("", ".", "..") for part in path.parts):
        raise PathPolicyError("empty, dot, and parent path segments are forbidden")
    return path


def resolve_within_root(root: Path, value: str) -> Path:
    relative = validate_relative_posix_path(value)
    root_resolved = root.resolve(strict=True)
    candidate = (root_resolved / Path(*relative.parts)).resolve(strict=False)
    try:
        common = Path(os.path.commonpath([root_resolved, candidate]))
    except ValueError as exc:
        raise PathPolicyError("path is on a different volume") from exc
    if common != root_resolved:
        raise PathPolicyError("path or symlink escapes the declared root")
    return candidate
