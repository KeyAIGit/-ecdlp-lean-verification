"""Small immutable value types shared by the P04 orchestrator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class OrchestrationError(ValueError):
    """A fail-closed campaign, registry, provenance, or record error."""

    def __init__(self, code: str, path: str, message: str) -> None:
        if not all(isinstance(value, str) and value for value in (code, path, message)):
            raise TypeError("orchestration error fields must be non-empty strings")
        self.code = code
        self.path = path
        self.message = message
        super().__init__(f"{code} {path}: {message}")


@dataclass(frozen=True, order=True)
class DependencyManifestEntry:
    """One exact repository file in an implementation manifest."""

    path: str
    sha256: str
    size_bytes: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
        }


@dataclass(frozen=True)
class DependencyManifest:
    """Sorted file manifest whose digest is over the complete entry list."""

    entries: tuple[DependencyManifestEntry, ...]
    sha256: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "manifest_kind": "ecdlp_lab_dependency_manifest_v1",
            "entries": [entry.as_dict() for entry in self.entries],
            "sha256": self.sha256,
        }


@dataclass(frozen=True)
class MethodDescriptor:
    """Data-only allowlist row.  It intentionally has no executable locator."""

    method_id: str

    def as_dict(self) -> dict[str, str]:
        return {"method_id": self.method_id}


@dataclass(frozen=True)
class CampaignPlan:
    """A validated campaign and its complete deterministic work expansion."""

    campaign: dict[str, Any]
    work_units: tuple[dict[str, Any], ...]

    def work_for_method(self, method_id: str) -> dict[str, Any]:
        matches = tuple(
            work
            for work in self.work_units
            if work.get("identity", {}).get("method_id") == method_id
        )
        if len(matches) != 1:
            raise OrchestrationError(
                "orchestration.work.lookup",
                "$.identity.method_id",
                "method must identify exactly one work unit in this campaign",
            )
        return matches[0]


__all__ = [
    "CampaignPlan",
    "DependencyManifest",
    "DependencyManifestEntry",
    "MethodDescriptor",
    "OrchestrationError",
]
