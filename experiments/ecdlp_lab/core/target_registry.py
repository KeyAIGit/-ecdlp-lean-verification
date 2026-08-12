"""Fail-closed authority for committed public/private engineering targets."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable

from .candidate_validation import validate_candidate
from .canonical import is_sha256, load_json, sha256_file
from .catalog_registry import resolve_curve_fixture, trusted_catalog_sha256s
from .contracts import (
    ValidationContext,
    derive_target_vector_id,
    validate_cross_record_bundle,
)
from .paths import PathSafetyError, resolve_artifact_path


LAB_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPO_ROOT = LAB_ROOT.parents[1]
TARGET_REGISTRY_PATH = (
    "experiments/ecdlp_lab/fixtures/targets/target_registry_v1.json"
)
TARGET_REGISTRY_RAW_SHA256 = (
    "5e2619f0d91752d11adfc9a6035a8f8eebb218037b0125f1bcdfba29df663d78"
)
TARGET_REGISTRY_KIND = "ecdlp_lab_target_registry_v1"

# Compatibility names for the original P01/P04 singleton authority.
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

_ROOT_KEYS = frozenset({"schema_version", "registry_kind", "entry_count", "entries"})
_ENTRY_KEYS = frozenset(
    {
        "curve_catalog_sha256",
        "curve_fixture_id",
        "private_path",
        "private_raw_sha256",
        "private_target_vector_sha256",
        "public_path",
        "public_raw_sha256",
        "public_target_vector_sha256",
        "source_kind",
    }
)


class TargetRegistryError(ValueError):
    """The target trust root is missing, malformed, or byte-drifted."""


@dataclass(frozen=True, order=True)
class TargetAuthority:
    public_target_vector_sha256: str
    private_target_vector_sha256: str
    public_path: str
    private_path: str
    public_raw_sha256: str
    private_raw_sha256: str
    curve_catalog_sha256: str
    curve_fixture_id: str
    source_kind: str


@dataclass(frozen=True)
class TargetPair:
    """Byte-verified pair with copy-out access to mutable JSON values."""

    _public_record: dict[str, Any] = field(repr=False)
    _private_record: dict[str, Any] = field(repr=False)
    authority: TargetAuthority | None = field(default=None, repr=False)

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


def _object(value: Any, keys: frozenset[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or frozenset(value) != keys:
        raise TargetRegistryError(f"{label}: object key set drifted")
    return value


def _load_fixed(
    root: Path, relative_path: str, raw_sha256: str, label: str
) -> dict[str, Any]:
    try:
        path = resolve_artifact_path(root, relative_path, must_exist=True)
        if path.is_symlink() or not path.is_file():
            raise TargetRegistryError(f"{label}: target must be a nonsymlink regular file")
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


def load_target_registry(
    *, repo_root: Path | str = DEFAULT_REPO_ROOT
) -> tuple[TargetAuthority, ...]:
    root = Path(repo_root)
    document = _load_fixed(
        root, TARGET_REGISTRY_PATH, TARGET_REGISTRY_RAW_SHA256, "target registry"
    )
    _object(document, _ROOT_KEYS, "target registry")
    if document["schema_version"] != 1 or document["registry_kind"] != TARGET_REGISTRY_KIND:
        raise TargetRegistryError("target registry protocol drifted")
    rows = document["entries"]
    if not isinstance(rows, list) or document["entry_count"] != len(rows) or len(rows) != 7:
        raise TargetRegistryError("target registry must contain exactly seven authorities")
    authorities: list[TargetAuthority] = []
    for index, value in enumerate(rows):
        row = _object(value, _ENTRY_KEYS, f"target registry entry {index}")
        for name in (
            "public_target_vector_sha256",
            "private_target_vector_sha256",
            "public_raw_sha256",
            "private_raw_sha256",
            "curve_catalog_sha256",
        ):
            if not is_sha256(row[name]):
                raise TargetRegistryError(f"target registry entry {index}: {name} is invalid")
        for name in ("public_path", "private_path", "curve_fixture_id", "source_kind"):
            if not isinstance(row[name], str) or not row[name]:
                raise TargetRegistryError(f"target registry entry {index}: {name} is invalid")
        authorities.append(TargetAuthority(**row))
    if authorities != sorted(authorities):
        raise TargetRegistryError("target registry entries must be sorted by public identity")
    public_ids = [item.public_target_vector_sha256 for item in authorities]
    private_ids = [item.private_target_vector_sha256 for item in authorities]
    paths = [path for item in authorities for path in (item.public_path, item.private_path)]
    if len(set(public_ids)) != len(public_ids) or len(set(private_ids)) != len(private_ids):
        raise TargetRegistryError("target registry contains duplicate semantic identities")
    if len(set(paths)) != len(paths):
        raise TargetRegistryError("target registry contains duplicate record paths")
    return tuple(authorities)


def _assert_pair_semantics(
    public: dict[str, Any],
    private: dict[str, Any],
    authority: TargetAuthority,
    *,
    repo_root: Path,
    known_public_ids: frozenset[str],
) -> None:
    if public.get("branch") != "public" or private.get("branch") != "private_validator_only":
        raise TargetRegistryError("target branches do not form a public/private pair")
    try:
        public_id = derive_target_vector_id(public)
        private_id = derive_target_vector_id(private)
    except ValueError as error:
        raise TargetRegistryError(f"target semantic identity is invalid: {error}") from error
    if public_id != authority.public_target_vector_sha256 or public.get("target_vector_id") != public_id:
        raise TargetRegistryError("public target semantic identity drifted")
    if private_id != authority.private_target_vector_sha256 or private.get("target_vector_id") != private_id:
        raise TargetRegistryError("private target semantic identity drifted")
    public_payload = public.get("public_payload")
    private_payload = private.get("private_payload")
    if not isinstance(public_payload, dict) or not isinstance(private_payload, dict):
        raise TargetRegistryError("target pair lacks its branch-appropriate payload")
    if private_payload.get("public_target_vector_sha256") != public_id:
        raise TargetRegistryError("private target does not bind the public target")
    if public_payload.get("curve_catalog_sha256") != authority.curve_catalog_sha256:
        raise TargetRegistryError("target registry catalog binding drifted")
    if public_payload.get("curve_fixture_id") != authority.curve_fixture_id:
        raise TargetRegistryError("target registry fixture binding drifted")

    try:
        fixture = resolve_curve_fixture(
            authority.curve_catalog_sha256,
            authority.curve_fixture_id,
            repo_root=repo_root,
        )
    except (TypeError, ValueError) as error:
        raise TargetRegistryError(f"target curve is not registry-authorized: {error}") from error
    for key, expected in fixture.public_curve_payload().items():
        if public_payload.get(key) != expected:
            raise TargetRegistryError(f"public target curve field {key!r} drifted")
    if public_payload.get("source_kind") != fixture.source_kind:
        raise TargetRegistryError("public target curve source kind drifted")
    if public_payload.get("target_count") != 1:
        raise TargetRegistryError("each authority must contain exactly one target")

    expected_scalar = private_payload.get("expected_scalar")
    candidate_input = SimpleNamespace(
        p=fixture.field_p,
        a=fixture.curve_a,
        b=fixture.curve_b,
        G=fixture.generator,
        Q=tuple(public_payload.get("target", ())),
        ell=fixture.subgroup_order,
    )
    if not validate_candidate(candidate_input, expected_scalar).passed:
        raise TargetRegistryError("private scalar does not reproduce the public target")
    context = ValidationContext.from_records(
        (public, private),
        repo_root=repo_root,
        known_catalog_sha256s=trusted_catalog_sha256s(repo_root=repo_root),
        known_target_vector_sha256s=known_public_ids,
        verify_artifacts=False,
    )
    issues = validate_cross_record_bundle((public, private), context)
    if issues:
        first = issues[0]
        raise TargetRegistryError(
            f"target contract validation failed: {first.code} {first.path}: {first.message}"
        )


def load_target_pair(
    public_target_vector_sha256: str = PUBLIC_TARGET_VECTOR_SHA256,
    *,
    repo_root: Path | str = DEFAULT_REPO_ROOT,
) -> TargetPair:
    """Resolve one public identity only through the committed registry."""

    if not is_sha256(public_target_vector_sha256):
        raise TargetRegistryError("public target identity must be lowercase SHA-256")
    root = Path(repo_root)
    authorities = load_target_registry(repo_root=root)
    matches = [
        item
        for item in authorities
        if item.public_target_vector_sha256 == public_target_vector_sha256
    ]
    if len(matches) != 1:
        raise TargetRegistryError("public target identity is not authorized")
    authority = matches[0]
    public = _load_fixed(root, authority.public_path, authority.public_raw_sha256, "public")
    private = _load_fixed(root, authority.private_path, authority.private_raw_sha256, "private")
    _assert_pair_semantics(
        public,
        private,
        authority,
        repo_root=root,
        known_public_ids=frozenset(
            item.public_target_vector_sha256 for item in authorities
        ),
    )
    return TargetPair(deepcopy(public), deepcopy(private), authority)


def load_target_pairs(
    public_target_vector_sha256s: Iterable[str],
    *,
    repo_root: Path | str = DEFAULT_REPO_ROOT,
) -> tuple[TargetPair, ...]:
    if isinstance(public_target_vector_sha256s, (str, bytes)):
        raise TargetRegistryError("target identities must be an iterable of digests")
    ids = tuple(public_target_vector_sha256s)
    if not ids or len(ids) != len(set(ids)):
        raise TargetRegistryError("target identities must be nonempty and unique")
    return tuple(load_target_pair(item, repo_root=repo_root) for item in ids)


def known_target_vector_sha256s(
    *, repo_root: Path | str = DEFAULT_REPO_ROOT
) -> frozenset[str]:
    """Return public identities; private identities never enter campaigns."""

    return frozenset(
        item.public_target_vector_sha256
        for item in load_target_registry(repo_root=repo_root)
    )


__all__ = [
    "PRIVATE_TARGET_PATH",
    "PRIVATE_TARGET_RAW_SHA256",
    "PRIVATE_TARGET_VECTOR_SHA256",
    "PUBLIC_TARGET_PATH",
    "PUBLIC_TARGET_RAW_SHA256",
    "PUBLIC_TARGET_VECTOR_SHA256",
    "TARGET_REGISTRY_PATH",
    "TARGET_REGISTRY_RAW_SHA256",
    "TargetAuthority",
    "TargetPair",
    "TargetRegistryError",
    "known_target_vector_sha256s",
    "load_target_pair",
    "load_target_pairs",
    "load_target_registry",
]
