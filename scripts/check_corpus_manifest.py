#!/usr/bin/env python3
"""Validate every corpus manifest referenced by domains/registry.json.

Zero third-party dependencies. This gate validates structure, integrity metadata,
version relations, effective counts, and the boundary between literature intake
and research authorization. It does not claim that the literature is complete or
that the claims inside a paper are true.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "domains" / "registry.json"
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
RELATION_TYPES = {"supersedes", "superseded_by", "supports", "contradicts", "extends", "reproduces"}
PRIMARY_STATUS = {"available", "missing"}
STORAGE_STATUS = {"drive_primary", "secondary_dossier_only", "remote_primary_verified", "local_verified_pending_drive_pdf"}
THREAT_MODELS = {"classical_plain_ecdlp", "implementation_or_auxiliary_input", "fault_tolerant_quantum_ecdlp", "context_or_foundation"}
CLAIM_STATUS = {"not_started", "blocked_missing_primary", "abstract_and_metadata_only", "in_progress", "complete"}


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"missing file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")


def validate_delta_source(tag: str, src: dict) -> list[str]:
    errors: list[str] = []
    sid = src.get("source_id")
    prefix = f"{tag}: source {sid!r}"
    if not isinstance(sid, str) or not ID_RE.fullmatch(sid):
        errors.append(f"{prefix}: invalid source_id")
        return errors
    for field in (
        "title", "year", "priority", "topic", "threat_models", "primary_status",
        "storage_status", "current_version", "identifiers", "artifact", "source_card",
        "claim_extraction_status", "relations", "provenance",
    ):
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
    return errors


def validate_manifest(path: Path, expected_domain: str) -> list[str]:
    errors: list[str] = []
    try:
        manifest = load(path)
    except ValueError as exc:
        return [str(exc)]
    tag = path.relative_to(ROOT).as_posix()

    if manifest.get("schema_version") != "1.0":
        errors.append(f"{tag}: schema_version must be 1.0")
    if manifest.get("domain_id") != expected_domain:
        errors.append(f"{tag}: domain_id {manifest.get('domain_id')!r} != registry id {expected_domain!r}")
    if not manifest.get("manifest_id"):
        errors.append(f"{tag}: missing manifest_id")

    baseline = manifest.get("baseline_snapshot")
    if not isinstance(baseline, dict):
        return errors + [f"{tag}: baseline_snapshot must be an object"]
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

    delta_sources: list[dict] = []
    relations: list[dict] = []
    seen_snapshot_ids: set[str] = set()
    for snapshot in manifest.get("delta_snapshots") or []:
        snap_id = snapshot.get("id")
        if not snap_id or snap_id in seen_snapshot_ids:
            errors.append(f"{tag}: missing or duplicate delta snapshot id {snap_id!r}")
        seen_snapshot_ids.add(snap_id)
        added = snapshot.get("added_sources")
        if not isinstance(added, list):
            errors.append(f"{tag}: {snap_id}: added_sources must be a list")
            continue
        for src in added:
            errors.extend(validate_delta_source(f"{tag}: {snap_id}", src))
            delta_sources.append(src)
        relations.extend(snapshot.get("relations") or [])
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
    for rel in relations:
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
        "quantum_track": baseline_quantum + sum("fault_tolerant_quantum_ecdlp" in (src.get("threat_models") or []) for src in delta_sources),
    }
    if manifest.get("effective_counts") != computed:
        errors.append(f"{tag}: effective_counts drift: committed={manifest.get('effective_counts')} computed={computed}")

    policy = manifest.get("policy") or {}
    required_true = (
        "append_only_source_history", "supersession_does_not_delete",
        "metadata_card_is_not_accepted_claim", "threat_models_must_not_mix",
        "experiments_require_decision_gate", "negative_results_are_retained",
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
    print(f"corpus-manifest check OK: {checked} registered manifest(s), snapshot integrity and version relations consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
