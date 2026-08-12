"""Byte-pinned, data-only P04 method allowlist."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from experiments.ecdlp_lab.core.canonical import load_json, sha256_file
from experiments.ecdlp_lab.core.paths import PathSafetyError, resolve_artifact_path
from experiments.ecdlp_lab.methods.python.model import METHOD_IDS

from .model import MethodDescriptor, OrchestrationError


LAB_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPO_ROOT = LAB_ROOT.parents[1]
METHOD_ALLOWLIST_PATH = (
    "experiments/ecdlp_lab/fixtures/orchestration/method_allowlist_v1.json"
)
METHOD_ALLOWLIST_RAW_SHA256 = (
    "d3d0e29a19125246787c0837609e23d0fe6658d35b51131bf5630b13ac24cec5"
)
METHOD_ALLOWLIST_KIND = "ecdlp_lab_method_allowlist_v1"

_ROOT_KEYS = frozenset({"schema_version", "registry_kind", "methods"})
_ROW_KEYS = frozenset({"method_id"})


def _error(path: str, message: str) -> OrchestrationError:
    return OrchestrationError("orchestration.allowlist", path, message)


def _exact_object(value: Any, keys: frozenset[str], path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error(path, "must be an object")
    if frozenset(value) != keys:
        raise _error(path, "key set drifted")
    return value


def load_method_allowlist(
    *, repo_root: Path | str = DEFAULT_REPO_ROOT
) -> tuple[MethodDescriptor, ...]:
    """Verify and load the fixed method ID list; no executable data is accepted."""

    try:
        path = resolve_artifact_path(repo_root, METHOD_ALLOWLIST_PATH, must_exist=True)
        if not path.is_file():
            raise _error("$.registry", "allowlist must be a regular file")
        if sha256_file(path) != METHOD_ALLOWLIST_RAW_SHA256:
            raise _error("$.registry", "raw allowlist bytes drifted")
        document = load_json(path)
    except OrchestrationError:
        raise
    except (OSError, PathSafetyError, TypeError, ValueError) as error:
        raise _error("$.registry", f"cannot load fixed allowlist: {error}") from error

    root = _exact_object(document, _ROOT_KEYS, "$")
    if root.get("schema_version") != 1:
        raise _error("$.schema_version", "must equal 1")
    if root.get("registry_kind") != METHOD_ALLOWLIST_KIND:
        raise _error("$.registry_kind", "registry kind drifted")
    rows = root.get("methods")
    if not isinstance(rows, list):
        raise _error("$.methods", "must be an array")

    descriptors: list[MethodDescriptor] = []
    for index, value in enumerate(rows):
        row = _exact_object(value, _ROW_KEYS, f"$.methods[{index}]")
        method_id = row.get("method_id")
        if not isinstance(method_id, str) or method_id not in METHOD_IDS:
            raise _error(
                f"$.methods[{index}].method_id",
                "method is not a frozen P03 implementation",
            )
        descriptors.append(MethodDescriptor(method_id))

    ids = tuple(descriptor.method_id for descriptor in descriptors)
    if ids != tuple(sorted(METHOD_IDS)):
        raise _error("$.methods", "must contain exactly the sorted frozen P03 method IDs")
    return tuple(descriptors)


def allowed_method_ids(
    *, repo_root: Path | str = DEFAULT_REPO_ROOT
) -> frozenset[str]:
    return frozenset(
        descriptor.method_id
        for descriptor in load_method_allowlist(repo_root=repo_root)
    )


def resolve_method(
    method_id: str, *, repo_root: Path | str = DEFAULT_REPO_ROOT
) -> MethodDescriptor:
    """Resolve an exact ID without normalization, paths, commands, or argv."""

    if not isinstance(method_id, str):
        raise _error("$.method_id", "must be an exact string")
    matches = tuple(
        descriptor
        for descriptor in load_method_allowlist(repo_root=repo_root)
        if descriptor.method_id == method_id
    )
    if len(matches) != 1:
        raise _error("$.method_id", "method is not allowlisted")
    return matches[0]


__all__ = [
    "METHOD_ALLOWLIST_KIND",
    "METHOD_ALLOWLIST_PATH",
    "METHOD_ALLOWLIST_RAW_SHA256",
    "allowed_method_ids",
    "load_method_allowlist",
    "resolve_method",
]
