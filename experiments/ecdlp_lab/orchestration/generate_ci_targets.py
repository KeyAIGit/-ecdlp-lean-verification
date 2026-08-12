"""Generate the committed P04C CI target registry and its split records.

The public half contains only the curve, generator, and target.  The scalar and
derivation seed live exclusively in the private-validator half.  All output is
canonical JSON; observational telemetry is intentionally absent.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

from experiments.ecdlp_lab.core.canonical import (
    canonical_json_bytes,
    load_json,
    sha256_bytes,
    sha256_file,
    sha256_json,
)
from experiments.ecdlp_lab.core.catalog_registry import resolve_curve_fixture
from experiments.framework.ec_oracle import Curve as OracleCurve


LAB_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPO_ROOT = LAB_ROOT.parents[1]
SPEC_PATH = "experiments/ecdlp_lab/fixtures/targets/ci_target_spec_v1.json"
TARGET_ROOT = "experiments/ecdlp_lab/fixtures/targets/records"
REGISTRY_PATH = "experiments/ecdlp_lab/fixtures/targets/target_registry_v1.json"
GENERATOR_PATH = "experiments/ecdlp_lab/orchestration/generate_ci_targets.py"
ORACLE_PATH = "experiments/framework/ec_oracle.py"

LEGACY_PUBLIC_PATH = (
    "experiments/ecdlp_lab/fixtures/contracts/valid/target_vector_public_v1.json"
)
LEGACY_PRIVATE_PATH = (
    "experiments/ecdlp_lab/fixtures/contracts/valid/target_vector_private_v1.json"
)

_COMMON = {
    "schema_version": 1,
    "record_kind": "lab_engineering_fixture",
    "contract_kind": "target_vector_v1",
    "internal_classification": "engineering_only",
    "framework_authorization_class": "fixture",
    "hypothesis_id": None,
    "candidate_id": None,
    "authorization_id": None,
    "native_research_outcome": False,
    "route_effect": "none",
    "retention_class": "engineering_only",
    "retainable": False,
}


def _derive_scalar(domain: str, fixture_id: str, subgroup_order: int) -> tuple[str, int]:
    seed = hashlib.sha256(f"{domain}/{fixture_id}".encode("ascii")).hexdigest()
    scalar = 1 + int(seed[:16], 16) % (subgroup_order - 1)
    return seed, scalar


def _provenance(spec: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    config_sha = sha256_file(repo_root / SPEC_PATH)
    producer_sha = sha256_file(repo_root / GENERATOR_PATH)
    validator_sha = sha256_file(repo_root / ORACLE_PATH)
    snapshot = sha256_json(
        {
            "catalog_sha256": spec["catalog_sha256"],
            "config_sha256": config_sha,
            "producer_sha256": producer_sha,
            "validator_sha256": validator_sha,
        }
    )
    diff = sha256_json(
        {
            "base_commit": spec["base_commit"],
            "config_sha256": config_sha,
            "source_snapshot_sha256": snapshot,
        }
    )
    return {
        "source_commit": spec["base_commit"],
        "source_tree_clean": False,
        "source_snapshot_sha256": snapshot,
        "producer_dependency_sha256s": [producer_sha],
        "validator_dependency_sha256s": [validator_sha],
        "config_sha256": config_sha,
        "diff_sha256": diff,
    }


def _pair_for_fixture(
    fixture_id: str,
    *,
    catalog_sha256: str,
    scalar_domain: str,
    provenance: dict[str, Any],
    repo_root: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    fixture = resolve_curve_fixture(catalog_sha256, fixture_id, repo_root=repo_root)
    seed, scalar = _derive_scalar(scalar_domain, fixture_id, fixture.subgroup_order)
    curve = OracleCurve(fixture.field_p, fixture.curve_a, fixture.curve_b)
    target = curve.scalar_mul(scalar, fixture.generator)
    if target is None:
        raise ValueError(f"derived target is infinity for {fixture_id}")
    public_payload = {
        **fixture.public_curve_payload(),
        "curve_catalog_sha256": fixture.catalog_sha256,
        "source_kind": fixture.source_kind,
        "target": list(target),
        "target_count": 1,
        "public_scalar_interval": None,
    }
    public_id = sha256_json(public_payload)
    generation_receipt = sha256_json(
        {
            "curve_catalog_sha256": fixture.catalog_sha256,
            "curve_fixture_id": fixture.fixture_id,
            "expected_scalar": scalar,
            "generator": list(fixture.generator),
            "public_target_vector_sha256": public_id,
            "target": list(target),
            "target_derivation_seed": seed,
        }
    )
    private_payload = {
        "expected_scalar": scalar,
        "generation_receipt_sha256": generation_receipt,
        "public_target_vector_sha256": public_id,
        "target_derivation_seed": seed,
        "validator_use_only": True,
    }
    private_id = sha256_json(private_payload)
    public = {
        **_COMMON,
        "provenance": provenance,
        "target_vector_id": public_id,
        "branch": "public",
        "public_payload": public_payload,
        "private_payload": None,
    }
    private = {
        **_COMMON,
        "provenance": provenance,
        "target_vector_id": private_id,
        "branch": "private_validator_only",
        "public_payload": None,
        "private_payload": private_payload,
    }
    return public, private


def generate(*, repo_root: Path | str = DEFAULT_REPO_ROOT) -> dict[str, bytes]:
    root = Path(repo_root).resolve(strict=True)
    spec = load_json(root / SPEC_PATH)
    if not isinstance(spec, dict):
        raise ValueError("target spec must be an object")
    expected_keys = {
        "base_commit",
        "catalog_sha256",
        "fixture_ids",
        "scalar_derivation_domain",
        "schema_version",
        "spec_kind",
        "target_count_per_fixture",
    }
    if set(spec) != expected_keys:
        raise ValueError("target spec key set drifted")
    if spec["schema_version"] != 1 or spec["spec_kind"] != "ecdlp_lab_ci_target_spec_v1":
        raise ValueError("target spec protocol drifted")
    fixture_ids = spec["fixture_ids"]
    if (
        not isinstance(fixture_ids, list)
        or len(fixture_ids) != 6
        or fixture_ids != sorted(set(fixture_ids))
        or spec["target_count_per_fixture"] != 1
    ):
        raise ValueError("target spec must name the six sorted CI fixtures exactly once")
    provenance = _provenance(spec, root)
    outputs: dict[str, bytes] = {}
    entries: list[dict[str, Any]] = []

    legacy_public = load_json(root / LEGACY_PUBLIC_PATH)
    legacy_private = load_json(root / LEGACY_PRIVATE_PATH)
    entries.append(
        {
            "curve_catalog_sha256": legacy_public["public_payload"]["curve_catalog_sha256"],
            "curve_fixture_id": legacy_public["public_payload"]["curve_fixture_id"],
            "private_path": LEGACY_PRIVATE_PATH,
            "private_raw_sha256": sha256_file(root / LEGACY_PRIVATE_PATH),
            "private_target_vector_sha256": legacy_private["target_vector_id"],
            "public_path": LEGACY_PUBLIC_PATH,
            "public_raw_sha256": sha256_file(root / LEGACY_PUBLIC_PATH),
            "public_target_vector_sha256": legacy_public["target_vector_id"],
            "source_kind": "legacy_p01_contract_fixture",
        }
    )

    for fixture_id in fixture_ids:
        public, private = _pair_for_fixture(
            fixture_id,
            catalog_sha256=spec["catalog_sha256"],
            scalar_domain=spec["scalar_derivation_domain"],
            provenance=provenance,
            repo_root=root,
        )
        public_path = f"{TARGET_ROOT}/{fixture_id}.public.json"
        private_path = f"{TARGET_ROOT}/{fixture_id}.private.json"
        public_bytes = canonical_json_bytes(public)
        private_bytes = canonical_json_bytes(private)
        outputs[public_path] = public_bytes
        outputs[private_path] = private_bytes
        entries.append(
            {
                "curve_catalog_sha256": spec["catalog_sha256"],
                "curve_fixture_id": fixture_id,
                "private_path": private_path,
                "private_raw_sha256": sha256_bytes(private_bytes),
                "private_target_vector_sha256": private["target_vector_id"],
                "public_path": public_path,
                "public_raw_sha256": sha256_bytes(public_bytes),
                "public_target_vector_sha256": public["target_vector_id"],
                "source_kind": "committed_ci_target_fixture",
            }
        )
    entries.sort(key=lambda row: row["public_target_vector_sha256"])
    registry = {
        "schema_version": 1,
        "registry_kind": "ecdlp_lab_target_registry_v1",
        "entry_count": len(entries),
        "entries": entries,
    }
    outputs[REGISTRY_PATH] = canonical_json_bytes(registry)
    return outputs


def _write_or_check(outputs: dict[str, bytes], *, repo_root: Path, check: bool) -> None:
    drift: list[str] = []
    for relative_path, expected in sorted(outputs.items()):
        path = repo_root / relative_path
        if check:
            if not path.is_file() or path.read_bytes() != expected:
                drift.append(relative_path)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(expected)
    if drift:
        raise SystemExit("target fixture drift: " + ", ".join(drift))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    root = DEFAULT_REPO_ROOT.resolve(strict=True)
    outputs = generate(repo_root=root)
    _write_or_check(outputs, repo_root=root, check=args.check)
    registry_sha = sha256_bytes(outputs[REGISTRY_PATH])
    print(f"CI target registry pass: {len(outputs) - 1} records, sha256={registry_sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["REGISTRY_PATH", "SPEC_PATH", "generate", "main"]
