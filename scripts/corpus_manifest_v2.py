#!/usr/bin/env python3
"""Versioned corpus-manifest validator for the KeyAI Research OS.

The validator has no third-party dependencies. It supports both the original
embedded v1.0 manifest and the scalable v1.1 layout, where an index manifest
references one immutable baseline snapshot plus append-only delta files.

It validates structure, integrity metadata, source-version relations, counts,
threat-model boundaries, and the separation between literature intake and
research authorization. It does not certify literature completeness or the
truth of claims inside a source.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "domains" / "registry.json"
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
RELATION_TYPES = {"supersedes", "superseded_by", "supports", "contradicts", "extends", "reproduces"}
PRIMARY_STATUS = {"available", "missing"}
STORAGE_STATUS = {
    "drive_primary",
    "secondary_dossier_only",
    "remote_primary_verified",
    "local_verified_pending_drive_pdf",
}
THREAT_MODELS = {
    "classical_plain_ecdlp",
    "implementation_or_auxiliary_input",
    "fault_tolerant_quantum_ecdlp",
    "context_or_foundation",
}
CLAIM_STATUS = {
    "not_started",
    "blocked_missing_primary",
    "abstract_and_metadata_only",
    "in_progress",
    "complete",
}


def load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"missing file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")


def repo_path(raw: str, *, tag: str) -> Path:
    if not isinstance(raw, str) or not raw:
        raise ValueError(f"{tag}: snapshot path must be a non-empty string")
    candidate = (ROOT / raw).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError:
        raise ValueError(f"{tag}: snapshot path escapes repository root: {raw!r}")
    return candidate


def resolve_snapshots(manifest: dict[str, Any], tag: str) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    refs = manifest.get("snapshot_files")
    if refs is None:
        baseline = manifest.get("baseline_snapshot")
        deltas = manifest.get("delta_snapshots")
        if manifest.get("schema_version") != "1.0":
            errors.append(f"{tag}: embedded snapshots require schema_version 1.0")
        if not isinstance(baseline, dict):
            errors.append(f"{tag}: baseline_snapshot must be an object")
            baseline = {}
        if not isinstance(deltas, list):
            errors.append(f"{tag}: delta_snapshots must be a list")
            deltas = []
        return baseline, deltas, errors

    if manifest.get("schema_version") != "1.1":
        errors.append(f"{tag}: snapshot_files require schema_version 1.1")
    if "baseline_snapshot" in manifest or "delta_snapshots" in manifest:
        errors.append(f"{tag}: do not mix embedded snapshots with snapshot_files")
    if not isinstance(refs, dict):
        return {}, [], errors + [f"{tag}: snapshot_files must be an object"]

    baseline_ref = refs.get("baseline")
    delta_refs = refs.get("deltas")
    if not isinstance(delta_refs, list) or not delta_refs:
        errors.append(f"{tag}: snapshot_files.deltas must be a non-empty list")
        delta_refs = []
    all_refs = [baseline_ref, *delta_refs]
    string_refs = [ref for ref in all_refs if isinstance(ref, str)]
    if len(string_refs) != len(set(string_refs)):
        errors.append(f"{tag}: duplicate snapshot file reference")

    try:
        baseline = load(repo_path(baseline_ref, tag=tag))
    except ValueError as exc:
        errors.append(str(exc))
        baseline = {}
    if baseline.get("snapshot_kind") != "baseline":
        errors.append(f"{tag}: referenced baseline must declare snapshot_kind=baseline")
    if baseline.get("schema_version") != 1:
        errors.append(f"{tag}: referenced baseline schema_version must be 1")

    deltas: list[dict[str, Any]] = []
    for ref in delta_refs:
        try:
            snapshot = load(repo_path(ref, tag=tag))
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if snapshot.get("snapshot_kind") != "delta":
            errors.append(f"{tag}: {ref}: snapshot_kind must be delta")
        if snapshot.get("schema_version") != 1:
            errors.append(f"{tag}: {ref}: snapshot schema_version must be 1")
        deltas.append(snapshot)
    return baseline, deltas, errors


def validate_delta_source(tag: str, snapshot_id: str, src: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    sid = src.get("source_id")
    prefix = f"{tag}: {snapshot_id}: source {sid!r}"
    if not isinstance(sid, str) or not ID_RE.fullmatch(sid):
        return [f"{prefix}: invalid source_id"]

    required = (
        "title",
        "year",
        "priority",
        "topic",
        "threat_models",
        "primary_status",
        "storage_status",
        "current_version",
        "identifiers",
        "artifact",
        "source_card",
        "claim_extraction_status",
        "relations",
        "provenance",
        "review_boundary",
        "reported_results",
    )
    for field in required:
        if field not in src:
            errors.append(f"{prefix}: missing field {field}")

    if src.get("priority") not in {"P0", "P1"}:
        errors.append(f"{prefix}: invalid priority {src.get('priority')!r}")
    if src.get("primary_status") not in PRIMARY_STATUS:
        errors.append(f"{prefix}: invalid primary_status {src.get('primary_status')!r}")
    if src.get("storage_status") not in STORAGE_STATUS:
        errors.append(f"{prefix}: invalid storage_status {src.get('storage_status')!r}")
    if src.get("claim_extraction_status") not in CLAIM_STATUS:
        errors.append(f"{prefix}: invalid claim_extraction_status {src.get('claim_extraction_status')!r}")
    if not isinstance(src.get("current_version"), bool):
        errors.append(f"{prefix}: current_version must be boolean")

    threat_models = src.get("threat_models")
    if not isinstance(threat_models, list) or not threat_models:
        errors.append(f"{prefix}: threat_models must be a non-empty list")
    else:
        unknown = sorted(set(threat_models) - THREAT_MODELS)
        if unknown:
            errors.append(f"{prefix}: unknown threat_models {unknown}")

    artifact = src.get("artifact") or {}
    digest = artifact.get("sha256")
    if digest is not None and not HEX64.fullmatch(str(digest)):
        errors.append(f"{prefix}: sha256 must be null or 64 lowercase hex characters")
    if src.get("storage_status") in {"drive_primary", "local_verified_pending_drive_pdf"}:
        for field in ("official_url", "sha256", "pages", "bytes"):
            if not artifact.get(field):
                errors.append(f"{prefix}: storage_status requires artifact.{field}")
    if src.get("storage_status") == "drive_primary" and not artifact.get("drive_file_id"):
        errors.append(f"{prefix}: drive_primary requires artifact.drive_file_id")
    if src.get("primary_status") == "missing":
        if src.get("storage_status") != "secondary_dossier_only":
            errors.append(f"{prefix}: missing primary must use secondary_dossier_only")
        if src.get("claim_extraction_status") != "blocked_missing_primary":
            errors.append(f"{prefix}: missing primary must remain blocked_missing_primary")

    provenance = src.get("provenance") or {}
    if provenance.get("introduced_in_snapshot") != snapshot_id:
        errors.append(f"{prefix}: provenance.introduced_in_snapshot must equal {snapshot_id!r}")

    results = src.get("reported_results")
    if not isinstance(results, list) or not results:
        errors.append(f"{prefix}: reported_results must be a non-empty list")
    else:
        for index, result in enumerate(results):
            if not isinstance(result, dict) or not all(result.get(k) not in (None, "") for k in ("metric", "condition", "value")):
                errors.append(f"{prefix}: reported_results[{index}] needs metric, condition, and value")

    discrepancy = src.get("version_discrepancy")
    if discrepancy is not None:
        if not isinstance(discrepancy, dict):
            errors.append(f"{prefix}: version_discrepancy must be an object")
        else:
            preferred = discrepancy.get("preferred_version")
            observed = discrepancy.get("observed_versions")
            if not isinstance(preferred, str) or not preferred:
                errors.append(f"{prefix}: version_discrepancy requires preferred_version")
            if not isinstance(observed, list) or len(observed) < 2:
                errors.append(f"{prefix}: version_discrepancy requires at least two observed_versions")
            else:
                version_ids = [item.get("id") for item in observed if isinstance(item, dict)]
                if len(version_ids) != len(observed) or any(not isinstance(x, str) or not x for x in version_ids):
                    errors.append(f"{prefix}: every observed version requires a non-empty id")
                elif len(version_ids) != len(set(version_ids)):
                    errors.append(f"{prefix}: duplicate observed version id")
                elif preferred not in version_ids:
                    errors.append(f"{prefix}: preferred_version is not one of observed_versions")
                roles = [item.get("role") for item in observed if isinstance(item, dict)]
                if "current_corrected_numeric_source" not in roles:
                    errors.append(f"{prefix}: version_discrepancy lacks a current_corrected_numeric_source")
    return errors


def validate_manifest(path: Path, expected_domain: str) -> list[str]:
    errors: list[str] = []
    try:
        manifest = load(path)
    except ValueError as exc:
        return [str(exc)]
    tag = path.relative_to(ROOT).as_posix()

    if manifest.get("schema_version") not in {"1.0", "1.1"}:
        errors.append(f"{tag}: unsupported schema_version {manifest.get('schema_version')!r}")
    if manifest.get("domain_id") != expected_domain:
        errors.append(f"{tag}: domain_id {manifest.get('domain_id')!r} != registry id {expected_domain!r}")
    if not manifest.get("manifest_id"):
        errors.append(f"{tag}: missing manifest_id")

    baseline, snapshots, resolution_errors = resolve_snapshots(manifest, tag)
    errors.extend(resolution_errors)

    baseline_ids = baseline.get("source_ids")
    if not isinstance(baseline_ids, list) or not baseline_ids:
        errors.append(f"{tag}: baseline source_ids must be a non-empty list")
        baseline_ids = []
    if len(baseline_ids) != len(set(baseline_ids)):
        errors.append(f"{tag}: duplicate source id in baseline snapshot")
    invalid_base = [sid for sid in baseline_ids if not isinstance(sid, str) or not ID_RE.fullmatch(sid)]
    if invalid_base:
        errors.append(f"{tag}: invalid baseline source ids: {invalid_base}")
    if baseline.get("source_count") != len(baseline_ids):
        errors.append(f"{tag}: baseline source_count drift")
    for artifact in baseline.get("artifacts") or []:
        if not artifact.get("name"):
            errors.append(f"{tag}: baseline artifact missing name")
        if not isinstance(artifact.get("bytes"), int) or artifact["bytes"] <= 0:
            errors.append(f"{tag}: baseline artifact {artifact.get('name')}: invalid bytes")
        if not HEX64.fullmatch(str(artifact.get("sha256", ""))):
            errors.append(f"{tag}: baseline artifact {artifact.get('name')}: invalid sha256")

    delta_sources: list[dict[str, Any]] = []
    top_relations: list[dict[str, Any]] = []
    seen_snapshot_ids: set[str] = set()
    for snapshot in snapshots:
        snap_id = snapshot.get("id")
        if not isinstance(snap_id, str) or not ID_RE.fullmatch(snap_id):
            errors.append(f"{tag}: invalid delta snapshot id {snap_id!r}")
            snap_id = str(snap_id)
        if snap_id in seen_snapshot_ids:
            errors.append(f"{tag}: duplicate delta snapshot id {snap_id!r}")
        seen_snapshot_ids.add(snap_id)
        added = snapshot.get("added_sources")
        if not isinstance(added, list):
            errors.append(f"{tag}: {snap_id}: added_sources must be a list")
            continue
        for src in added:
            if not isinstance(src, dict):
                errors.append(f"{tag}: {snap_id}: source entry must be an object")
                continue
            errors.extend(validate_delta_source(tag, snap_id, src))
            delta_sources.append(src)
        relations = snapshot.get("relations")
        if not isinstance(relations, list):
            errors.append(f"{tag}: {snap_id}: relations must be a list")
        else:
            top_relations.extend(relations)
        impact = str(snapshot.get("decision_impact", "")).lower()
        if "does not authorize" not in impact and "no new classical proposal selected" not in impact:
            errors.append(f"{tag}: {snap_id}: decision_impact must preserve the experiment authorization boundary")

    delta_ids = [src.get("source_id") for src in delta_sources if isinstance(src.get("source_id"), str)]
    if len(delta_ids) != len(set(delta_ids)):
        errors.append(f"{tag}: duplicate source id across delta snapshots")
    collisions = sorted(set(baseline_ids) & set(delta_ids))
    if collisions:
        errors.append(f"{tag}: delta source ids already exist in baseline: {collisions}")
    all_ids = set(baseline_ids) | set(delta_ids)

    relation_keys: set[tuple[str, str, str]] = set()
    for rel in top_relations:
        source = rel.get("source_id")
        target = rel.get("target_source_id")
        rtype = rel.get("type")
        if rtype not in RELATION_TYPES:
            errors.append(f"{tag}: invalid relation type {rtype!r}")
        if source not in all_ids or target not in all_ids:
            errors.append(f"{tag}: relation {source!r} {rtype!r} {target!r} references unknown source")
        key = (str(source), str(rtype), str(target))
        if key in relation_keys:
            errors.append(f"{tag}: duplicate relation {key}")
        relation_keys.add(key)

    for src in delta_sources:
        source = src.get("source_id")
        for rel in src.get("relations") or []:
            rtype = rel.get("type")
            target = rel.get("target_source_id", rel.get("source_id"))
            if rtype not in RELATION_TYPES:
                errors.append(f"{tag}: source {source!r}: invalid embedded relation type {rtype!r}")
            if target not in all_ids:
                errors.append(f"{tag}: source {source!r}: embedded relation targets unknown source {target!r}")

    inverse = {"supersedes": "superseded_by", "superseded_by": "supersedes"}
    for source, rtype, target in relation_keys:
        if rtype in inverse and (target, inverse[rtype], source) not in relation_keys:
            errors.append(f"{tag}: relation {(source, rtype, target)} lacks reciprocal edge")

    superseded_ids = {source for source, rtype, _ in relation_keys if rtype == "superseded_by"}
    baseline_available = int(baseline.get("primary_available", 0))
    baseline_missing = int(baseline.get("missing_primary", 0))
    baseline_quantum = int(baseline.get("quantum_track", 0))
    computed = {
        "sources": len(baseline_ids) + len(delta_sources),
        "primary_available": baseline_available + sum(src.get("primary_status") == "available" for src in delta_sources),
        "missing_primary": baseline_missing + sum(src.get("primary_status") == "missing" for src in delta_sources),
        "current_versions": len(all_ids) - len(superseded_ids),
        "superseded_versions": len(superseded_ids),
        "quantum_track": baseline_quantum
        + sum("fault_tolerant_quantum_ecdlp" in (src.get("threat_models") or []) for src in delta_sources),
    }
    if manifest.get("effective_counts") != computed:
        errors.append(f"{tag}: effective_counts drift: committed={manifest.get('effective_counts')} computed={computed}")

    policy = manifest.get("policy") or {}
    required_true = (
        "append_only_source_history",
        "supersession_does_not_delete",
        "metadata_card_is_not_accepted_claim",
        "threat_models_must_not_mix",
        "experiments_require_decision_gate",
        "negative_results_are_retained",
    )
    for field in required_true:
        if policy.get(field) is not True:
            errors.append(f"{tag}: policy.{field} must be true")

    if expected_domain == "ecdlp-secp256k1":
        target = manifest.get("target") or {}
        if target.get("curve") != "secp256k1":
            errors.append(f"{tag}: ECDLP reference manifest must pin curve=secp256k1")
        if target.get("primary_threat_model") != "classical_plain_ecdlp":
            errors.append(f"{tag}: ECDLP target must keep classical_plain_ecdlp primary")
    return errors


def main() -> int:
    try:
        registry = load(REGISTRY)
    except ValueError as exc:
        print(f"corpus-manifest check FAILED:\n- {exc}")
        return 1
    errors: list[str] = []
    checked = 0
    for domain in registry.get("domains", []):
        rel = domain.get("corpus_manifest")
        if rel is None:
            continue
        checked += 1
        errors.extend(validate_manifest(ROOT / rel, domain.get("id")))
    if checked == 0:
        errors.append("domains/registry.json references no corpus_manifest")
    if errors:
        print("corpus-manifest check FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        f"corpus-manifest check OK: {checked} registered manifest(s), "
        "snapshot files, integrity metadata, counts, and version relations consistent"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
