#!/usr/bin/env python3
"""Deterministic synthetic secp256k1 pair generator for the ML structure probe.

This is a data-engineering qualification tool, not a discrete-log solver.  Every
record is synthetic and consists of:

    32-byte big-endian scalar d || 33-byte compressed point Q = [d]G

The producer uses OpenSSL through ``cryptography``.  The validator deliberately
uses a separate pure-Python Jacobian implementation for spot checks.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from cryptography.hazmat.backends.openssl.backend import backend as openssl_backend
from cryptography.hazmat.primitives.asymmetric import ec


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SECP256K1_N = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16
)
RECORD_SIZE = 65
DERIVATION_DOMAIN = b"keyai/ml-structure-probe/scalar/v1\0"


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def derive_scalar(master_seed: bytes, split: str, index: int) -> int:
    """Uniform rejection sample in [1,n-1], domain separated by split and index."""
    split_bytes = split.encode("ascii")
    counter = 0
    while True:
        digest = hashlib.sha256(
            DERIVATION_DOMAIN
            + master_seed
            + len(split_bytes).to_bytes(1, "big")
            + split_bytes
            + index.to_bytes(8, "big")
            + counter.to_bytes(4, "big")
        ).digest()
        value = int.from_bytes(digest, "big")
        if 0 < value < SECP256K1_N:
            return value
        counter += 1


def compressed_public_key(scalar: int) -> bytes:
    numbers = ec.derive_private_key(scalar, ec.SECP256K1()).public_key().public_numbers()
    return bytes((2 | (numbers.y & 1),)) + numbers.x.to_bytes(32, "big")


def _build_shard(job: dict[str, Any]) -> dict[str, Any]:
    output_root = Path(job["output_root"])
    relative_path = Path(job["relative_path"])
    final_path = output_root / relative_path
    final_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = final_path.with_suffix(final_path.suffix + f".tmp-{os.getpid()}")

    seed = bytes.fromhex(job["master_seed_hex"])
    split = str(job["split"])
    start = int(job["start"])
    count = int(job["count"])

    payload = bytearray(RECORD_SIZE * count)
    offset = 0
    for index in range(start, start + count):
        scalar = derive_scalar(seed, split, index)
        payload[offset : offset + 32] = scalar.to_bytes(32, "big")
        payload[offset + 32 : offset + RECORD_SIZE] = compressed_public_key(scalar)
        offset += RECORD_SIZE

    temporary_path.write_bytes(payload)
    os.replace(temporary_path, final_path)
    return {
        "split": split,
        "part": int(job["part"]),
        "start_index": start,
        "record_count": count,
        "relative_path": relative_path.as_posix(),
        "byte_count": len(payload),
        "sha256": sha256_bytes(payload),
    }


def git_state() -> dict[str, Any]:
    def run(*args: str) -> str:
        completed = subprocess.run(
            args,
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()

    try:
        commit = run("git", "rev-parse", "HEAD")
        status = run("git", "status", "--porcelain", "--untracked-files=no")
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "tracked_files_dirty": None}
    return {"commit": commit, "tracked_files_dirty": bool(status)}


def load_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schema_version",
        "experiment_id",
        "curve",
        "record_format",
        "master_seed_hex",
        "splits",
        "shard_records",
        "workers",
    }
    missing = sorted(required - set(config))
    if missing:
        raise ValueError(f"config missing fields: {missing}")
    if config["schema_version"] != 1:
        raise ValueError("unsupported config schema_version")
    if config["curve"] != "secp256k1":
        raise ValueError("P0 generator supports only synthetic secp256k1")
    if config["record_format"] != "scalar32-compressed-point33-v1":
        raise ValueError("unsupported record format")
    seed = bytes.fromhex(config["master_seed_hex"])
    if len(seed) != 32:
        raise ValueError("master_seed_hex must encode exactly 32 bytes")
    if not config["splits"] or any(int(v) <= 0 for v in config["splits"].values()):
        raise ValueError("every split must contain at least one record")
    if int(config["shard_records"]) <= 0:
        raise ValueError("shard_records must be positive")
    return config


def make_jobs(config: dict[str, Any], output_root: Path) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    shard_records = int(config["shard_records"])
    for split, raw_count in config["splits"].items():
        total = int(raw_count)
        part = 0
        for start in range(0, total, shard_records):
            count = min(shard_records, total - start)
            jobs.append(
                {
                    "output_root": str(output_root),
                    "relative_path": f"{split}/part-{part:05d}.bin",
                    "master_seed_hex": config["master_seed_hex"],
                    "split": split,
                    "part": part,
                    "start": start,
                    "count": count,
                }
            )
            part += 1
    return jobs


def generate(config_path: Path, output_root: Path) -> Path:
    config = load_config(config_path)
    output_root.mkdir(parents=True, exist_ok=True)
    jobs = make_jobs(config, output_root)
    workers = max(1, min(int(config["workers"]), len(jobs)))

    started = time.perf_counter()
    if workers == 1:
        shards = [_build_shard(job) for job in jobs]
    else:
        context = mp.get_context("spawn")
        with context.Pool(processes=workers) as pool:
            shards = list(pool.imap_unordered(_build_shard, jobs))
    elapsed = time.perf_counter() - started
    shards.sort(key=lambda item: (item["split"], item["part"]))

    source_files = [
        HERE / "generate_dataset.py",
        HERE / "validate_dataset.py",
        HERE / "probe.py",
        config_path,
    ]
    total_records = sum(int(item["record_count"]) for item in shards)
    manifest_without_hash = {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "dataset_role": "synthetic_data_engineering_qualification",
        "scientific_evidence": False,
        "curve": "secp256k1",
        "record_format": config["record_format"],
        "record_size_bytes": RECORD_SIZE,
        "private_data_origin": "deterministic synthetic scalars; no wallet data",
        "derivation": {
            "hash": "SHA-256",
            "method": "domain-separated rejection sampling into [1,n-1]",
            "domain": DERIVATION_DOMAIN.decode("ascii").rstrip("\0"),
            "master_seed_sha256": sha256_bytes(
                bytes.fromhex(config["master_seed_hex"])
            ),
            "split_domains": sorted(config["splits"]),
        },
        "config": config_path.relative_to(ROOT).as_posix(),
        "config_sha256": sha256_file(config_path),
        "source_state": git_state(),
        "source_hashes": {
            path.relative_to(ROOT).as_posix(): sha256_file(path)
            for path in source_files
        },
        "runtime": {
            "python": platform.python_version(),
            "cryptography": __import__("cryptography").__version__,
            "openssl": openssl_backend.openssl_version_text(),
            "platform": platform.platform(),
            "workers": workers,
        },
        "splits": {
            split: int(count) for split, count in config["splits"].items()
        },
        "total_records": total_records,
        "total_bytes": total_records * RECORD_SIZE,
        "generation": {
            "elapsed_seconds": round(elapsed, 6),
            "records_per_second": round(total_records / elapsed, 3),
        },
        "shards": shards,
    }
    manifest = dict(manifest_without_hash)
    manifest["dataset_root_sha256"] = sha256_bytes(canonical_json(shards))
    manifest["manifest_sha256"] = sha256_bytes(canonical_json(manifest_without_hash))
    manifest_path = output_root / "dataset_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    manifest_path = generate(args.config.resolve(), args.output_dir.resolve())
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    print(
        json.dumps(
            {
                "manifest": str(manifest_path),
                "records": manifest["total_records"],
                "bytes": manifest["total_bytes"],
                "seconds": manifest["generation"]["elapsed_seconds"],
                "records_per_second": manifest["generation"]["records_per_second"],
                "dataset_root_sha256": manifest["dataset_root_sha256"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
