"""Fail-closed authority loader for committed ECDLP lab curve catalogs.

Catalog bytes do not authorize themselves.  The one committed registry binds
their repository paths and raw SHA-256 digests; callers receive an authority
only after every registry entry and its optional generation spec has been
resolved beneath the repository root and verified byte-for-byte.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .canonical import is_sha256, load_json, sha256_file
from .paths import PathSafetyError, resolve_artifact_path

if TYPE_CHECKING:
    from experiments.ecdlp_lab.curves.model import ResolvedCurveFixture


LAB_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPO_ROOT = LAB_ROOT.parents[1]
REGISTRY_PATH = "experiments/ecdlp_lab/fixtures/curves/catalog_registry_v1.json"

REGISTRY_KIND = "ecdlp_lab_curve_catalog_registry_v1"
LEGACY_CATALOG_ID = "legacy_p1_curve_catalog"
CI_CATALOG_ID = "ecdlp_lab_ci_curve_catalog_v1"
CI_CATALOG_PATH = "experiments/ecdlp_lab/fixtures/curves/ci_curve_catalog_v1.json"
CI_SPEC_PATH = "experiments/ecdlp_lab/fixtures/curves/ci_catalog_spec_v1.json"
LEGACY_CATALOG_PATH = (
    "experiments/ml_structure_probe/reports/p1_toy_scaling/curve_catalog.json"
)

_REGISTRY_KEYS = frozenset({"schema_version", "registry_kind", "catalogs"})
_ENTRY_KEYS = frozenset(
    {
        "catalog_id",
        "source_kind",
        "path",
        "sha256",
        "curve_count",
        "spec_path",
        "spec_sha256",
    }
)
_EXPECTED_ENTRIES = {
    CI_CATALOG_ID: ("committed_lab_catalog", 6, CI_CATALOG_PATH, CI_SPEC_PATH),
    LEGACY_CATALOG_ID: (
        "read_only_legacy_catalog",
        40,
        LEGACY_CATALOG_PATH,
        None,
    ),
}
_CI_CATALOG_KEYS = frozenset(
    {
        "schema_version",
        "catalog_kind",
        "classification",
        "native_research_outcome",
        "spec_sha256",
        "curve_count",
        "field_bits",
        "families",
        "limits",
        "fixtures",
    }
)


class CatalogRegistryError(ValueError):
    """The committed catalog authority is missing, malformed, or drifted."""


@dataclass(frozen=True)
class CatalogAuthority:
    """One byte-verified catalog entry from the committed trust registry."""

    catalog_id: str
    source_kind: str
    path: str
    sha256: str
    curve_count: int
    spec_path: str | None
    spec_sha256: str | None
    resolved_path: Path
    resolved_spec_path: Path | None


def _fail(path: str, message: str) -> CatalogRegistryError:
    return CatalogRegistryError(f"{path}: {message}")


def _exact_keys(value: Any, expected: frozenset[str], path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _fail(path, "must be an object")
    actual = frozenset(value)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        raise _fail(path, f"key set drifted (missing={missing}, unknown={unknown})")
    return value


def _safe_regular_file(repo_root: Path, relative_path: Any, path: str) -> Path:
    if not isinstance(relative_path, str):
        raise _fail(path, "must be a repository-relative string")
    try:
        resolved = resolve_artifact_path(repo_root, relative_path, must_exist=True)
    except (OSError, PathSafetyError, TypeError, ValueError) as error:
        raise _fail(path, str(error)) from error
    if not resolved.is_file():
        raise _fail(path, "must resolve to a regular file")
    return resolved


def _verified_file(
    repo_root: Path,
    relative_path: Any,
    expected_sha256: Any,
    path: str,
) -> Path:
    if not is_sha256(expected_sha256):
        raise _fail(f"{path}.sha256", "must be a lowercase SHA-256 digest")
    resolved = _safe_regular_file(repo_root, relative_path, f"{path}.path")
    try:
        actual = sha256_file(resolved)
    except OSError as error:
        raise _fail(f"{path}.path", f"cannot hash file: {error}") from error
    if actual != expected_sha256:
        raise _fail(f"{path}.sha256", "raw file digest does not match registry")
    return resolved


def _verify_ci_catalog_binding(
    authority: CatalogAuthority, *, entry_path: str
) -> None:
    try:
        catalog = load_json(authority.resolved_path)
    except (OSError, ValueError) as error:
        raise _fail(f"{entry_path}.path", f"cannot parse strict CI catalog: {error}") from error
    catalog = _exact_keys(catalog, _CI_CATALOG_KEYS, f"{entry_path}.catalog")
    if catalog.get("schema_version") != 1:
        raise _fail(f"{entry_path}.catalog.schema_version", "must equal 1")
    if catalog.get("catalog_kind") != CI_CATALOG_ID:
        raise _fail(
            f"{entry_path}.catalog.catalog_kind",
            f"must equal {CI_CATALOG_ID!r}",
        )
    if catalog.get("classification") != "engineering_only":
        raise _fail(
            f"{entry_path}.catalog.classification", "must equal 'engineering_only'"
        )
    if catalog.get("native_research_outcome") is not False:
        raise _fail(
            f"{entry_path}.catalog.native_research_outcome", "must be false"
        )
    if catalog.get("spec_sha256") != authority.spec_sha256:
        raise _fail(
            f"{entry_path}.catalog.spec_sha256",
            "catalog does not bind the registry-authorized spec",
        )
    count = catalog.get("curve_count")
    fixtures = catalog.get("fixtures")
    if type(count) is not int or count != authority.curve_count:
        raise _fail(
            f"{entry_path}.catalog.curve_count",
            "catalog count differs from registry authority",
        )
    if not isinstance(fixtures, list) or len(fixtures) != authority.curve_count:
        raise _fail(
            f"{entry_path}.catalog.fixtures",
            "fixture array length differs from registry authority",
        )


def load_catalog_registry(
    *, repo_root: Path | str = DEFAULT_REPO_ROOT
) -> tuple[CatalogAuthority, ...]:
    """Load and byte-verify the fixed catalog registry and every entry.

    ``repo_root`` exists for isolated tests and checked-out repository mirrors;
    the registry locator itself is fixed and cannot be supplied by a caller.
    """

    root = Path(repo_root)
    registry_file = _safe_regular_file(root, REGISTRY_PATH, "$.registry")
    try:
        registry = load_json(registry_file)
    except (OSError, ValueError) as error:
        raise _fail("$.registry", f"cannot parse strict JSON: {error}") from error
    registry = _exact_keys(registry, _REGISTRY_KEYS, "$")
    if registry.get("schema_version") != 1:
        raise _fail("$.schema_version", "must equal 1")
    if registry.get("registry_kind") != REGISTRY_KIND:
        raise _fail("$.registry_kind", f"must equal {REGISTRY_KIND!r}")
    rows = registry.get("catalogs")
    if not isinstance(rows, list):
        raise _fail("$.catalogs", "must be an array")
    if len(rows) != len(_EXPECTED_ENTRIES):
        raise _fail("$.catalogs", "must contain exactly the legacy and CI catalogs")

    authorities: list[CatalogAuthority] = []
    seen_digests: set[str] = set()
    seen_paths: set[str] = set()
    for index, raw_row in enumerate(rows):
        row_path = f"$.catalogs[{index}]"
        row = _exact_keys(raw_row, _ENTRY_KEYS, row_path)
        catalog_id = row.get("catalog_id")
        if catalog_id not in _EXPECTED_ENTRIES:
            raise _fail(f"{row_path}.catalog_id", "unknown catalog authority")
        source_kind, expected_count, expected_path, expected_spec_path = (
            _EXPECTED_ENTRIES[catalog_id]
        )
        has_spec = expected_spec_path is not None
        if row.get("source_kind") != source_kind:
            raise _fail(f"{row_path}.source_kind", "source kind drifted")
        curve_count = row.get("curve_count")
        if type(curve_count) is not int or curve_count != expected_count:
            raise _fail(f"{row_path}.curve_count", "curve count drifted")
        path = row.get("path")
        if not isinstance(path, str):
            raise _fail(f"{row_path}.path", "must be a string")
        if path != expected_path:
            raise _fail(f"{row_path}.path", "catalog path drifted")
        if path in seen_paths:
            raise _fail(f"{row_path}.path", "duplicate catalog path")
        seen_paths.add(path)
        digest = row.get("sha256")
        resolved = _verified_file(root, path, digest, row_path)
        if digest in seen_digests:
            raise _fail(f"{row_path}.sha256", "duplicate catalog digest")
        seen_digests.add(digest)

        spec_path = row.get("spec_path")
        spec_sha256 = row.get("spec_sha256")
        resolved_spec: Path | None = None
        if has_spec:
            if not isinstance(spec_path, str):
                raise _fail(f"{row_path}.spec_path", "CI catalog requires a spec path")
            if spec_path != expected_spec_path:
                raise _fail(f"{row_path}.spec_path", "catalog spec path drifted")
            if spec_path == path:
                raise _fail(f"{row_path}.spec_path", "spec and catalog paths must differ")
            if spec_path in seen_paths:
                raise _fail(f"{row_path}.spec_path", "duplicate registry file path")
            seen_paths.add(spec_path)
            resolved_spec = _verified_file(
                root, spec_path, spec_sha256, f"{row_path}.spec"
            )
        elif spec_path is not None or spec_sha256 is not None:
            raise _fail(
                row_path, "legacy catalog must have null spec_path and spec_sha256"
            )

        authority = CatalogAuthority(
            catalog_id=catalog_id,
            source_kind=source_kind,
            path=path,
            sha256=digest,
            curve_count=curve_count,
            spec_path=spec_path,
            spec_sha256=spec_sha256,
            resolved_path=resolved,
            resolved_spec_path=resolved_spec,
        )
        if has_spec:
            _verify_ci_catalog_binding(authority, entry_path=row_path)
        authorities.append(authority)

    identifiers = [authority.catalog_id for authority in authorities]
    if identifiers != sorted(_EXPECTED_ENTRIES):
        raise _fail("$.catalogs", "catalog rows must be sorted by catalog_id")
    return tuple(authorities)


def trusted_catalog_sha256s(
    *, repo_root: Path | str = DEFAULT_REPO_ROOT
) -> frozenset[str]:
    """Return only raw digests whose complete registry verification passed."""

    return frozenset(
        authority.sha256 for authority in load_catalog_registry(repo_root=repo_root)
    )


def resolve_catalog(
    catalog_sha256: str, *, repo_root: Path | str = DEFAULT_REPO_ROOT
) -> CatalogAuthority:
    """Resolve one trusted raw digest, rejecting unknown or malformed values."""

    if not is_sha256(catalog_sha256):
        raise CatalogRegistryError("catalog digest must be a lowercase SHA-256 value")
    matches = [
        authority
        for authority in load_catalog_registry(repo_root=repo_root)
        if authority.sha256 == catalog_sha256
    ]
    if len(matches) != 1:
        raise CatalogRegistryError("catalog digest is not authorized by the registry")
    return matches[0]


def resolve_curve_fixture(
    catalog_sha256: str,
    fixture_id: str,
    *,
    repo_root: Path | str = DEFAULT_REPO_ROOT,
) -> "ResolvedCurveFixture":
    """Resolve one public curve fixture through the complete registry authority.

    The digest is resolved before catalog-specific projection.  Consequently a
    caller cannot use a hard-coded P1 locator, an unregistered catalog copy, or
    a catalog whose sibling registry entry has drifted.  Both the committed CI
    fixtures and the frozen P1 generator/base-point locators project to the
    shared :class:`ResolvedCurveFixture` model.
    """

    if not isinstance(fixture_id, str) or not fixture_id:
        raise CatalogRegistryError("fixture identifier must be a non-empty string")
    authority = resolve_catalog(catalog_sha256, repo_root=repo_root)
    if authority.catalog_id == CI_CATALOG_ID:
        try:
            from experiments.ecdlp_lab.curves.model import ResolvedCurveFixture

            document = load_json(authority.resolved_path)
            fixtures = document.get("fixtures") if isinstance(document, dict) else None
            if not isinstance(fixtures, list):
                raise ValueError("CI catalog fixtures must be an array")
            matches = tuple(
                entry
                for entry in fixtures
                if isinstance(entry, dict) and entry.get("fixture_id") == fixture_id
            )
            if len(matches) != 1:
                raise KeyError("unknown or duplicate CI curve fixture")
            return ResolvedCurveFixture.from_catalog_entry(
                matches[0],
                catalog_sha256=authority.sha256,
                source_kind=authority.source_kind,
            )
        except (KeyError, OSError, TypeError, ValueError) as error:
            raise CatalogRegistryError(
                f"CI curve fixture {fixture_id!r} cannot be resolved: {error}"
            ) from error

    if authority.catalog_id == LEGACY_CATALOG_ID:
        try:
            from experiments.ecdlp_lab.curves.p1_adapter import (
                load_legacy_catalog,
                resolve_legacy_base_point,
                resolve_legacy_generator,
            )

            catalog = load_legacy_catalog(
                catalog_path=authority.path,
                catalog_sha256=authority.sha256,
                repo_root=repo_root,
            )
            generator_matches = tuple(
                (curve.field_bits, curve.curve_index, generator.generator_index)
                for curve in catalog.curves
                for generator in curve.generators
                if generator.generator_id == fixture_id
            )
            curve_matches = tuple(
                curve.curve_id for curve in catalog.curves if curve.curve_id == fixture_id
            )
            if len(generator_matches) + len(curve_matches) != 1:
                raise KeyError("unknown or duplicate legacy curve fixture")
            if generator_matches:
                field_bits, curve_index, generator_index = generator_matches[0]
                return resolve_legacy_generator(
                    field_bits,
                    curve_index,
                    generator_index,
                    catalog=catalog,
                )
            return resolve_legacy_base_point(curve_matches[0], catalog=catalog)
        except (KeyError, OSError, TypeError, ValueError) as error:
            raise CatalogRegistryError(
                f"legacy curve fixture {fixture_id!r} cannot be resolved: {error}"
            ) from error

    raise CatalogRegistryError("registry contains an unsupported catalog authority")


__all__ = [
    "CI_CATALOG_ID",
    "CI_CATALOG_PATH",
    "CI_SPEC_PATH",
    "LEGACY_CATALOG_ID",
    "LEGACY_CATALOG_PATH",
    "REGISTRY_PATH",
    "CatalogAuthority",
    "CatalogRegistryError",
    "load_catalog_registry",
    "resolve_catalog",
    "resolve_curve_fixture",
    "trusted_catalog_sha256s",
]
