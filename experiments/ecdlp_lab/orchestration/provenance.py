"""Content-addressed implementation manifests and contract provenance."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from experiments.ecdlp_lab.core.canonical import is_sha256, sha256_file, sha256_json
from experiments.ecdlp_lab.core.paths import (
    PathSafetyError,
    resolve_artifact_path,
    validate_repo_relative,
)
from experiments.ecdlp_lab.methods.python.model import METHOD_IDS

from .model import DependencyManifest, DependencyManifestEntry, OrchestrationError


LAB_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPO_ROOT = LAB_ROOT.parents[1]
P04_BASE_SOURCE_COMMIT = "1aba9f025950af687d9a0e5104c8642e018aeb2e"
DEVELOPMENT_DIFF_KIND = "ecdlp_lab_development_snapshot_diff_v1"

_COMMON_METHOD_PATHS = (
    "experiments/ecdlp_lab/__init__.py",
    "experiments/ecdlp_lab/core/__init__.py",
    "experiments/ecdlp_lab/core/canonical.py",
    "experiments/ecdlp_lab/core/catalog_registry.py",
    "experiments/ecdlp_lab/core/paths.py",
    "experiments/ecdlp_lab/curves/__init__.py",
    "experiments/ecdlp_lab/curves/model.py",
    "experiments/ecdlp_lab/curves/p1_adapter.py",
    "experiments/ecdlp_lab/methods/python/__init__.py",
    "experiments/ecdlp_lab/methods/python/counting.py",
    "experiments/ecdlp_lab/methods/python/dispatch.py",
    "experiments/ecdlp_lab/methods/python/model.py",
    "experiments/ecdlp_lab/orchestration/__init__.py",
    "experiments/ecdlp_lab/orchestration/events.py",
    "experiments/ecdlp_lab/orchestration/method_worker.py",
    "experiments/ml_structure_probe/p1_toy_scaling/__init__.py",
    "experiments/ml_structure_probe/p1_toy_scaling/curve_math.py",
)
_METHOD_PATHS = {
    "bsgs_v1": (*_COMMON_METHOD_PATHS, "experiments/ecdlp_lab/methods/python/bsgs.py"),
    "ordinary_rho_xmod3_v1": (
        *_COMMON_METHOD_PATHS,
        "experiments/ecdlp_lab/methods/python/rho.py",
    ),
}
_CORE_INITIALIZER_CLOSURE_PATHS = (
    "experiments/ecdlp_lab/core/canonical.py",
    "experiments/ecdlp_lab/core/contracts.py",
    "experiments/ecdlp_lab/core/issues.py",
    "experiments/ecdlp_lab/core/paths.py",
    "experiments/ecdlp_lab/core/safety.py",
    "experiments/ecdlp_lab/core/schema.py",
)
_VALIDATOR_PATHS = (
    "experiments/ecdlp_lab/__init__.py",
    "experiments/ecdlp_lab/core/__init__.py",
    "experiments/ecdlp_lab/core/candidate_validation.py",
    "experiments/ecdlp_lab/core/canonical.py",
    "experiments/ecdlp_lab/core/issues.py",
    "experiments/ecdlp_lab/orchestration/__init__.py",
    "experiments/ecdlp_lab/orchestration/events.py",
    "experiments/ecdlp_lab/orchestration/validator_worker.py",
    "experiments/framework/__init__.py",
    "experiments/framework/ec_oracle.py",
)
_METHOD_EXECUTION_PATHS = tuple(
    sorted(
        set(_CORE_INITIALIZER_CLOSURE_PATHS).union(
            *(_METHOD_PATHS[method_id] for method_id in sorted(_METHOD_PATHS))
        )
    )
)
_VALIDATOR_EXECUTION_PATHS = tuple(
    sorted(set(_VALIDATOR_PATHS).union(_CORE_INITIALIZER_CLOSURE_PATHS))
)
_SOURCE_SNAPSHOT_PATHS = (
    "experiments/ecdlp_lab/__init__.py",
    "experiments/ecdlp_lab/contracts/campaign_config_v1.schema.json",
    "experiments/ecdlp_lab/contracts/method_request_v1.schema.json",
    "experiments/ecdlp_lab/contracts/method_result_v1.schema.json",
    "experiments/ecdlp_lab/contracts/target_vector_v1.schema.json",
    "experiments/ecdlp_lab/contracts/validation_receipt_v1.schema.json",
    "experiments/ecdlp_lab/contracts/work_unit_v1.schema.json",
    "experiments/ecdlp_lab/core/__init__.py",
    "experiments/ecdlp_lab/core/candidate_validation.py",
    "experiments/ecdlp_lab/core/canonical.py",
    "experiments/ecdlp_lab/core/catalog_registry.py",
    "experiments/ecdlp_lab/core/contracts.py",
    "experiments/ecdlp_lab/core/issues.py",
    "experiments/ecdlp_lab/core/paths.py",
    "experiments/ecdlp_lab/core/safety.py",
    "experiments/ecdlp_lab/core/schema.py",
    "experiments/ecdlp_lab/core/target_registry.py",
    "experiments/ecdlp_lab/curves/__init__.py",
    "experiments/ecdlp_lab/curves/model.py",
    "experiments/ecdlp_lab/curves/p1_adapter.py",
    "experiments/ecdlp_lab/fixtures/contracts/valid/target_vector_private_v1.json",
    "experiments/ecdlp_lab/fixtures/contracts/valid/target_vector_public_v1.json",
    "experiments/ecdlp_lab/fixtures/curves/catalog_registry_v1.json",
    "experiments/ecdlp_lab/fixtures/orchestration/method_allowlist_v1.json",
    "experiments/ecdlp_lab/fixtures/targets/ci_target_spec_v1.json",
    "experiments/ecdlp_lab/fixtures/targets/target_registry_v1.json",
    "experiments/ecdlp_lab/methods/python/__init__.py",
    "experiments/ecdlp_lab/methods/python/bsgs.py",
    "experiments/ecdlp_lab/methods/python/counting.py",
    "experiments/ecdlp_lab/methods/python/dispatch.py",
    "experiments/ecdlp_lab/methods/python/model.py",
    "experiments/ecdlp_lab/methods/python/rho.py",
    "experiments/ecdlp_lab/orchestration/__init__.py",
    "experiments/ecdlp_lab/orchestration/allowlist.py",
    "experiments/ecdlp_lab/orchestration/events.py",
    "experiments/ecdlp_lab/orchestration/generate_ci_targets.py",
    "experiments/ecdlp_lab/orchestration/method_worker.py",
    "experiments/ecdlp_lab/orchestration/model.py",
    "experiments/ecdlp_lab/orchestration/process.py",
    "experiments/ecdlp_lab/orchestration/provenance.py",
    "experiments/ecdlp_lab/orchestration/public_handoff.py",
    "experiments/ecdlp_lab/orchestration/records.py",
    "experiments/ecdlp_lab/orchestration/run_smoke.py",
    "experiments/ecdlp_lab/orchestration/runner.py",
    "experiments/ecdlp_lab/orchestration/storage.py",
    "experiments/ecdlp_lab/orchestration/validator_worker.py",
    "experiments/framework/__init__.py",
    "experiments/framework/ec_oracle.py",
    "experiments/ml_structure_probe/p1_toy_scaling/__init__.py",
    "experiments/ml_structure_probe/p1_toy_scaling/curve_math.py",
)
_GIT_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def _error(path: str, message: str) -> OrchestrationError:
    return OrchestrationError("orchestration.provenance", path, message)


def build_dependency_manifest(
    paths: Iterable[str], *, repo_root: Path | str = DEFAULT_REPO_ROOT
) -> DependencyManifest:
    """Hash a sorted, duplicate-free set of confined regular files."""

    if isinstance(paths, (str, bytes)):
        raise _error("$.paths", "must be an iterable of repository-relative paths")
    try:
        materialized = tuple(paths)
    except TypeError as error:
        raise _error("$.paths", "must be iterable") from error
    if not materialized:
        raise _error("$.paths", "manifest must contain at least one path")
    if any(not isinstance(path, str) for path in materialized):
        raise _error("$.paths", "every manifest path must be a string")
    if len(set(materialized)) != len(materialized):
        raise _error("$.paths", "duplicate manifest paths are forbidden")

    entries: list[DependencyManifestEntry] = []
    for index, relative_path in enumerate(sorted(materialized)):
        try:
            canonical_path = validate_repo_relative(relative_path)
            resolved = resolve_artifact_path(
                repo_root, canonical_path, must_exist=True
            )
            if not resolved.is_file():
                raise _error(f"$.paths[{index}]", "dependency must be a regular file")
            size = resolved.stat().st_size
            digest = sha256_file(resolved)
        except OrchestrationError:
            raise
        except (OSError, PathSafetyError, TypeError, ValueError) as error:
            raise _error(f"$.paths[{index}]", str(error)) from error
        entries.append(DependencyManifestEntry(canonical_path, digest, size))

    projection = {
        "manifest_kind": "ecdlp_lab_dependency_manifest_v1",
        "entries": [entry.as_dict() for entry in entries],
    }
    return DependencyManifest(tuple(entries), sha256_json(projection))


def method_implementation_manifest(
    method_id: str, *, repo_root: Path | str = DEFAULT_REPO_ROOT
) -> DependencyManifest:
    if (
        not isinstance(method_id, str)
        or method_id not in METHOD_IDS
        or method_id not in _METHOD_PATHS
    ):
        raise _error("$.method_id", "method is not a frozen P03 implementation")
    # Importing ``methods.python`` eagerly imports both algorithms.  Therefore
    # both method IDs honestly share one executed implementation closure; the
    # method ID, not a fictional file-set distinction, separates work identity.
    return build_dependency_manifest(_METHOD_EXECUTION_PATHS, repo_root=repo_root)


def method_implementation_sha256(
    method_id: str, *, repo_root: Path | str = DEFAULT_REPO_ROOT
) -> str:
    return method_implementation_manifest(method_id, repo_root=repo_root).sha256


def method_execution_manifest(
    *, repo_root: Path | str = DEFAULT_REPO_ROOT
) -> DependencyManifest:
    """Bind the complete import closure executed by either method worker."""

    return build_dependency_manifest(_METHOD_EXECUTION_PATHS, repo_root=repo_root)


def method_execution_sha256(
    *, repo_root: Path | str = DEFAULT_REPO_ROOT
) -> str:
    return method_execution_manifest(repo_root=repo_root).sha256


def validator_implementation_manifest(
    *, repo_root: Path | str = DEFAULT_REPO_ROOT
) -> DependencyManifest:
    return build_dependency_manifest(_VALIDATOR_EXECUTION_PATHS, repo_root=repo_root)


def validator_implementation_sha256(
    *, repo_root: Path | str = DEFAULT_REPO_ROOT
) -> str:
    return validator_implementation_manifest(repo_root=repo_root).sha256


def validator_execution_manifest(
    *, repo_root: Path | str = DEFAULT_REPO_ROOT
) -> DependencyManifest:
    """Bind the independent validator worker and core initializer closure."""

    return build_dependency_manifest(_VALIDATOR_EXECUTION_PATHS, repo_root=repo_root)


def validator_execution_sha256(
    *, repo_root: Path | str = DEFAULT_REPO_ROOT
) -> str:
    return validator_execution_manifest(repo_root=repo_root).sha256


def source_snapshot_manifest(
    *, repo_root: Path | str = DEFAULT_REPO_ROOT
) -> DependencyManifest:
    """Hash the fixed contract/authority/orchestration source closure for P04."""

    return build_dependency_manifest(_SOURCE_SNAPSHOT_PATHS, repo_root=repo_root)


def development_diff_sha256(source_snapshot_sha256: str) -> str:
    """Bind the fixed merged-P04 base to one exact P04C source snapshot."""

    if not is_sha256(source_snapshot_sha256):
        raise _error(
            "$.source_snapshot_sha256", "must be a lowercase SHA-256 digest"
        )
    return sha256_json(
        {
            "base_source_commit": P04_BASE_SOURCE_COMMIT,
            "diff_kind": DEVELOPMENT_DIFF_KIND,
            "source_snapshot_sha256": source_snapshot_sha256,
        }
    )


def build_provenance(
    *,
    config_sha256: str,
    source_commit: str,
    source_tree_clean: bool,
    diff_sha256: str | None,
    producer_dependency_sha256s: Iterable[str],
    validator_dependency_sha256s: Iterable[str],
    source_snapshot_sha256: str,
) -> dict[str, object]:
    """Build one schema-compatible provenance object after strict validation."""

    if not is_sha256(config_sha256):
        raise _error("$.config_sha256", "must be a lowercase SHA-256 digest")
    if not isinstance(source_commit, str) or _GIT_COMMIT_RE.fullmatch(source_commit) is None:
        raise _error("$.source_commit", "must be a lowercase 40-hex commit")
    if type(source_tree_clean) is not bool:
        raise _error("$.source_tree_clean", "must be a boolean")
    if not is_sha256(source_snapshot_sha256):
        raise _error("$.source_snapshot_sha256", "must be a lowercase SHA-256 digest")
    if source_tree_clean:
        if diff_sha256 is not None:
            raise _error("$.diff_sha256", "clean source must have a null diff digest")
    elif not is_sha256(diff_sha256):
        raise _error("$.diff_sha256", "dirty source must bind a lowercase SHA-256 digest")

    try:
        producer = tuple(producer_dependency_sha256s)
        validator = tuple(validator_dependency_sha256s)
    except TypeError as error:
        raise _error("$", "dependency digests must be iterable") from error
    for label, values in (("producer", producer), ("validator", validator)):
        if not values or len(values) != len(set(values)) or any(
            not is_sha256(value) for value in values
        ):
            raise _error(
                f"$.{label}_dependency_sha256s",
                "must be a non-empty unique digest collection",
            )
    producer = tuple(sorted(producer))
    validator = tuple(sorted(validator))
    if set(producer) & set(validator):
        raise _error("$", "producer and validator dependency identities must differ")

    return {
        "source_commit": source_commit,
        "source_tree_clean": source_tree_clean,
        "source_snapshot_sha256": source_snapshot_sha256,
        "producer_dependency_sha256s": list(producer),
        "validator_dependency_sha256s": list(validator),
        "config_sha256": config_sha256,
        "diff_sha256": diff_sha256,
    }


def build_campaign_provenance(
    *,
    config_sha256: str,
    source_commit: str,
    source_tree_clean: bool,
    diff_sha256: str | None,
    method_ids: Iterable[str],
    repo_root: Path | str = DEFAULT_REPO_ROOT,
) -> dict[str, object]:
    """Build the fixed nonretainable P04C development provenance.

    ``source_tree_clean`` and ``diff_sha256`` remain in the call signature for
    compatibility with the P01 provenance builder API.  They are never
    trusted: the returned campaign provenance is always dirty and its diff
    digest is derived from the fixed merged-P04 base plus current source
    snapshot.
    """

    if source_commit != P04_BASE_SOURCE_COMMIT:
        raise _error(
            "$.source_commit", "P04C must anchor the fixed merged-P04 base commit"
        )
    if type(source_tree_clean) is not bool:
        raise _error("$.source_tree_clean", "must be a boolean")
    if diff_sha256 is not None and not is_sha256(diff_sha256):
        raise _error("$.diff_sha256", "must be null or a lowercase SHA-256")

    try:
        ids = tuple(method_ids)
    except TypeError as error:
        raise _error("$.method_ids", "must be iterable") from error
    if (
        not ids
        or any(not isinstance(method, str) for method in ids)
        or len(ids) != len(set(ids))
        or any(method not in METHOD_IDS for method in ids)
    ):
        raise _error("$.method_ids", "must be a non-empty unique frozen method set")
    producer = tuple(
        sorted(
            {
                method_implementation_sha256(method, repo_root=repo_root)
                for method in ids
            }
        )
    )
    validator = validator_implementation_sha256(repo_root=repo_root)
    snapshot = source_snapshot_manifest(repo_root=repo_root).sha256
    return build_provenance(
        config_sha256=config_sha256,
        source_commit=P04_BASE_SOURCE_COMMIT,
        source_tree_clean=False,
        diff_sha256=development_diff_sha256(snapshot),
        producer_dependency_sha256s=producer,
        validator_dependency_sha256s=(validator,),
        source_snapshot_sha256=snapshot,
    )


__all__ = [
    "DEVELOPMENT_DIFF_KIND",
    "P04_BASE_SOURCE_COMMIT",
    "build_campaign_provenance",
    "build_dependency_manifest",
    "build_provenance",
    "development_diff_sha256",
    "method_execution_manifest",
    "method_execution_sha256",
    "method_implementation_manifest",
    "method_implementation_sha256",
    "source_snapshot_manifest",
    "validator_implementation_manifest",
    "validator_implementation_sha256",
    "validator_execution_manifest",
    "validator_execution_sha256",
]
