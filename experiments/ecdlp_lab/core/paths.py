"""Path confinement helpers for lab artifacts.

The lab stores only POSIX-style, repository-relative locators.  These helpers
intentionally reject rather than normalize ambiguous input.
"""

from __future__ import annotations

import os
import re
from pathlib import Path, PurePosixPath
from typing import Any


class PathSafetyError(ValueError):
    """Raised when an artifact locator is outside the lab path boundary."""


_URI_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:")
_PERCENT_ESCAPE = re.compile(r"%[0-9A-Fa-f]{2}")


def reject_engine_destination(value: str | os.PathLike[str]) -> None:
    """Reject the repository's Engine state tree as a read or write target."""

    text = os.fspath(value).replace("\\", "/").strip("/")
    parts = tuple(part.casefold() for part in PurePosixPath(text).parts)
    for index in range(max(0, len(parts) - 1)):
        if parts[index : index + 2] == ("experiments", "engine"):
            raise PathSafetyError("Engine destinations are outside the lab boundary")
    if parts and parts[0] == "engine":
        raise PathSafetyError("Engine destinations are outside the lab boundary")


def reject_protected_destination(value: str | os.PathLike[str]) -> None:
    """Reject every owner-protected scientific or authorization destination."""

    text = os.fspath(value).replace("\\", "/").strip("/")
    folded = text.casefold()
    parts = folded.split("/") if folded else []
    reject_engine_destination(text)
    protected = (
        parts[:1] == ["data"],
        len(parts) >= 2
        and parts[0] == "repo"
        and parts[1].startswith("ecdlp_decision_substrate."),
        len(parts) >= 2
        and parts[0] == "repo"
        and parts[1].startswith("research_engine"),
        parts == ["repo", "ecdlp_typed_evidence_v0.json"],
        parts == ["repo", "research_claims_v0.json"],
        parts == ["experiments", "hypotheses.yaml"],
        bool(parts) and len(parts) == 1 and parts[0].startswith("verified") and parts[0].endswith(".md"),
        parts[:2] == ["ecdlp", "proved"],
    )
    if any(protected):
        raise PathSafetyError("destination is protected from lab writes and artifacts")


def validate_repo_relative(value: str | os.PathLike[str]) -> str:
    """Return an unchanged safe POSIX repository-relative path or raise.

    No normalization is performed: dot components, repeated separators,
    backslashes, URI syntax, Windows drives, and encoded escapes are rejected.
    """

    try:
        text = os.fspath(value)
    except TypeError as error:
        raise PathSafetyError("path must be a string or path-like value") from error
    if not isinstance(text, str):
        raise PathSafetyError("path must decode to text")
    if not text or text != text.strip():
        raise PathSafetyError("path must be non-empty and have no surrounding whitespace")
    if any(ord(character) < 32 or ord(character) == 127 for character in text):
        raise PathSafetyError("path contains a control character")
    if "\\" in text:
        raise PathSafetyError("backslashes and Windows paths are forbidden")
    if text.startswith(("/", "//", "~")) or _WINDOWS_DRIVE.match(text):
        raise PathSafetyError("absolute, home-relative, and Windows paths are forbidden")
    if "://" in text or _URI_SCHEME.match(text):
        raise PathSafetyError("URLs and URI schemes are forbidden")
    if _PERCENT_ESCAPE.search(text):
        raise PathSafetyError("percent-encoded path components are forbidden")
    raw_parts = text.split("/")
    if any(part in {"", ".", ".."} for part in raw_parts):
        raise PathSafetyError("empty and dot path components are forbidden")
    reject_protected_destination(text)
    return text


def resolve_artifact_path(
    repo_root: str | os.PathLike[str],
    relative_path: str | os.PathLike[str],
    *,
    must_exist: bool = False,
) -> Path:
    """Resolve a safe artifact path beneath ``repo_root`` without symlinks.

    Existing symlinks in any component are rejected, even when their resolved
    target remains below the root.  This provides one simple invariant for
    both reads and create-only writes and prevents symlink escape races in the
    normal single-process lab workflow.
    """

    relative = validate_repo_relative(relative_path)
    root_input = Path(repo_root)
    if not root_input.exists() or not root_input.is_dir():
        raise PathSafetyError("repository root must be an existing directory")
    if root_input.is_symlink():
        raise PathSafetyError("repository root must not be a symlink")
    root = root_input.resolve(strict=True)
    candidate = root.joinpath(*relative.split("/"))

    current = root
    for component in relative.split("/"):
        current = current / component
        try:
            if current.is_symlink():
                raise PathSafetyError(f"symlink path component is forbidden: {component}")
        except OSError as error:
            raise PathSafetyError(f"cannot inspect path component: {component}") from error

    try:
        resolved = candidate.resolve(strict=must_exist)
    except (OSError, RuntimeError) as error:
        raise PathSafetyError(f"artifact path cannot be resolved: {error}") from error
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise PathSafetyError("artifact path escapes the repository root") from error
    if must_exist and not resolved.exists():
        raise PathSafetyError("artifact path does not exist")
    return resolved


def artifact_location(record: Any) -> str | None:
    """Extract and validate an optional artifact-ref location."""

    if not isinstance(record, dict):
        raise PathSafetyError("artifact reference must be an object")
    location = record.get("location")
    if location is None:
        return None
    return validate_repo_relative(location)
