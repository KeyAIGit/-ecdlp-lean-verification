"""Fail-closed authority for the one committed P04 public/private target pair.

The filenames and raw byte digests are code-owned.  A campaign can select the
public semantic identifier, but it cannot redirect either half of the pair or
substitute bytes that merely reproduce the same JSON values.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from .candidate_validation import validate_candidate
from .canonical import load_json, sha256_file
from .catalog_registry import resolve_curve_fixture, trusted_catalog_sha256s
from .contracts import (
    ValidationContext,
    derive_target_vector_id,
    validate_cross_record_bundle,
)
from .paths import PathSafetyError, resolve_artifact_path


LAB_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPO_ROOT = LAB_ROOT.parents[1]

PUBLIC_TARGET_PATH = (
    "experiments/ecdlp_lab/fixtures/contracts/valid/target_vector_public_v1.json"
)
PRIVATE_TARGET_PATH = (
    "experiments/ecdlp_lab/fixtures/contracts/valid/target_vector_private_v1.json"
)
PUBLIC_TARGET_RAW_SHA256 = (
    "78c5d776842a4a74083d337cbd66ddb15f898ec9ad73cf6aa38a4268ba68a08d"
)
PRIVATE_TARGET_RAW_SHA256 = (
    "c5a04f05b47a30be319a192c5fbd6475ed089ed9379637f97214745bc6d37a5d"
)
PUBLIC_TARGET_VECTOR_SHA256 = (
    "f530af54bbc7c68523bef1abcf97853d7c635244c15f5c071f91857ecf8083d8"
)
PRIVATE_TARGET_VECTOR_SHA256 = (
    "90e941d2c14c4d2be5bb5dfcc48a7103be5177b029c638b8c0c782018d7038f4"
)


class TargetRegistryError(ValueError):
    """The fixed target authority is missing, malformed, or byte-drifted."""


@dataclass(frozen=True)
class TargetPair:
    """Byte-verified target pair with copy-out access to mutable JSON values."""

    _public_record: dict[str, Any] = field(repr=False)
    _private_record: dict[str, Any] = field(repr=False)

    @property
    def public_record(self) -> dict[str, Any]:
        return deepcopy(self._public_record)

    @property
    def private_record(self) -> dict[str, Any]:
        return deepcopy(self._private_record)

    @property
    def public_payload(self) -> dict[str, Any]:
        return deepcopy(self._public_record["public_payload"])

    @property
    def private_payload(self) -> dict[str, Any]:
        return deepcopy(self._private_record["private_payload"])

    @property
    def public_target_vector_sha256(self) -> str:
        return self._public_record["target_vector_id"]

    @property
    def private_target_vector_sha256(self) -> str:
        return self._private_record["target_vector_id"]


def _load_fixed(
    root: Path, relative_path: str, raw_sha256: str, label: str
) -> dict[str, Any]:
    try:
        path = resolve_artifact_path(root, relative_path, must_exist=True)
        if not path.is_file():
            raise TargetRegistryError(f"{label}: target must be a regular file")
        if sha256_file(path) != raw_sha256:
            raise TargetRegistryError(f"{label}: raw target bytes drifted")
        record = load_json(path)
    except TargetRegistryError:
        raise
    except (OSError, PathSafetyError, TypeError, ValueError) as error:
        raise TargetRegistryError(f"{label}: cannot load fixed target: {error}") from error
    if not isinstance(record, dict):
        raise TargetRegistryError(f"{label}: target record must be an object")
    return record


def _assert_pair_semantics(
    public: dict[str, Any], private: dict[str, Any], *, repo_root: Path
) -> None:
    if public.get("branch") != "public" or private.get("branch") != "private_validator_only":
        raise TargetRegistryError("target branches are not the fixed public/private pair")
    try:
        public_id = derive_target_vector_id(public)
        private_id = derive_target_vector_id(private)
    except ValueError as error:
        raise TargetRegistryError(f"target semantic identity is invalid: {error}") from error
    if public_id != PUBLIC_TARGET_VECTOR_SHA256 or public.get("target_vector_id") != public_id:
        raise TargetRegistryError("public target semantic identity drifted")
    if private_id != PRIVATE_TARGET_VECTOR_SHA256 or private.get("target_vector_id") != private_id:
        raise TargetRegistryError("private target semantic identity drifted")

    public_payload = public.get("public_payload")
    private_payload = private.get("private_payload")
    if not isinstance(public_payload, dict) or not isinstance(private_payload, dict):
        raise TargetRegistryError("target pair lacks its branch-appropriate payload")
    if private_payload.get("public_target_vector_sha256") != public_id:
        raise TargetRegistryError("private target does not bind the authorized public target")

    try:
        fixture = resolve_curve_fixture(
            public_payload.get("curve_catalog_sha256"),
            public_payload.get("curve_fixture_id"),
            repo_root=repo_root,
        )
    except (TypeError, ValueError) as error:
        raise TargetRegistryError(
            f"public target curve is not registry-authorized: {error}"
        ) from error
    expected_curve = fixture.public_curve_payload()
    for key, expected in expected_curve.items():
        if public_payload.get(key) != expected:
            raise TargetRegistryError(f"public target curve field {key!r} drifted")
    if public_payload.get("curve_catalog_sha256") != fixture.catalog_sha256:
        raise TargetRegistryError("public target catalog digest drifted")
    if public_payload.get("source_kind") != fixture.source_kind:
        raise TargetRegistryError("public target source kind drifted")
    if public_payload.get("target_count") != 1:
        raise TargetRegistryError("P04 authority requires exactly one public target")

    expected_scalar = private_payload.get("expected_scalar")
    candidate_input = SimpleNamespace(
        p=fixture.field_p,
        a=fixture.curve_a,
        b=fixture.curve_b,
        G=fixture.generator,
        Q=tuple(public_payload.get("target", ())),
        ell=fixture.subgroup_order,
    )
    validation = validate_candidate(candidate_input, expected_scalar)
    if not validation.passed:
        raise TargetRegistryError("private expected scalar does not reproduce the public target")

    context = ValidationContext.from_records(
        (public, private),
        repo_root=repo_root,
        known_catalog_sha256s=trusted_catalog_sha256s(repo_root=repo_root),
        known_target_vector_sha256s=(PUBLIC_TARGET_VECTOR_SHA256,),
        verify_artifacts=False,
    )
    issues = validate_cross_record_bundle((public, private), context)
    if issues:
        first = issues[0]
        raise TargetRegistryError(
            f"target contract validation failed: {first.code} {first.path}: {first.message}"
        )


def load_target_pair(*, repo_root: Path | str = DEFAULT_REPO_ROOT) -> TargetPair:
    """Load the only authorized P04 pair from fixed paths and fixed raw digests."""

    root = Path(repo_root)
    public = _load_fixed(root, PUBLIC_TARGET_PATH, PUBLIC_TARGET_RAW_SHA256, "public")
    private = _load_fixed(root, PRIVATE_TARGET_PATH, PRIVATE_TARGET_RAW_SHA256, "private")
    _assert_pair_semantics(public, private, repo_root=root)
    return TargetPair(deepcopy(public), deepcopy(private))


def known_target_vector_sha256s() -> frozenset[str]:
    """Return public target authority; private identities never enter campaigns."""

    return frozenset({PUBLIC_TARGET_VECTOR_SHA256})


__all__ = [
    "PRIVATE_TARGET_PATH",
    "PRIVATE_TARGET_RAW_SHA256",
    "PRIVATE_TARGET_VECTOR_SHA256",
    "PUBLIC_TARGET_PATH",
    "PUBLIC_TARGET_RAW_SHA256",
    "PUBLIC_TARGET_VECTOR_SHA256",
    "TargetPair",
    "TargetRegistryError",
    "known_target_vector_sha256s",
    "load_target_pair",
]
