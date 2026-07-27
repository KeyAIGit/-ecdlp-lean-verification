#!/usr/bin/env python3
"""Independent-path validator for ML structure-probe pair datasets.

The validator does not import the producer.  It verifies every shard hash and
record, performs duplicate and gross-distribution checks, rederives selected
scalars, and recomputes selected public keys with separate pure-Python Jacobian
arithmetic.

This supplies path and artifact replay for data engineering.  It is not a claim
of source-independent scientific validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
P = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16)
N = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16)
GX = int("79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798", 16)
GY = int("483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8", 16)
RECORD_SIZE = 65
DERIVATION_DOMAIN = b"keyai/ml-structure-probe/scalar/v1\0"
SMALL_MODULI = (3, 5, 7, 11, 13)


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def derive_scalar(master_seed: bytes, split: str, index: int) -> int:
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
        if 0 < value < N:
            return value
        counter += 1


def jacobian_double(point: tuple[int, int, int]) -> tuple[int, int, int]:
    x, y, z = point
    if z == 0 or y == 0:
        return (0, 1, 0)
    yy = y * y % P
    s = 4 * x * yy % P
    m = 3 * x * x % P
    x3 = (m * m - 2 * s) % P
    yyyy = yy * yy % P
    y3 = (m * (s - x3) - 8 * yyyy) % P
    z3 = 2 * y * z % P
    return (x3, y3, z3)


def jacobian_add_affine(
    point: tuple[int, int, int], affine: tuple[int, int]
) -> tuple[int, int, int]:
    x1, y1, z1 = point
    x2, y2 = affine
    if z1 == 0:
        return (x2, y2, 1)
    z1z1 = z1 * z1 % P
    u2 = x2 * z1z1 % P
    s2 = y2 * z1 * z1z1 % P
    h = (u2 - x1) % P
    r = (s2 - y1) % P
    if h == 0:
        return jacobian_double(point) if r == 0 else (0, 1, 0)
    hh = h * h % P
    hhh = h * hh % P
    v = x1 * hh % P
    x3 = (r * r - hhh - 2 * v) % P
    y3 = (r * (v - x3) - y1 * hhh) % P
    z3 = z1 * h % P
    return (x3, y3, z3)


def scalar_mul_generator(scalar: int) -> tuple[int, int]:
    result = (0, 1, 0)
    for bit in bin(scalar)[2:]:
        result = jacobian_double(result)
        if bit == "1":
            result = jacobian_add_affine(result, (GX, GY))
    x, y, z = result
    if z == 0:
        raise ValueError("unexpected point at infinity")
    z_inv = pow(z, P - 2, P)
    z2 = z_inv * z_inv % P
    return (x * z2 % P, y * z2 * z_inv % P)


def sample_indices(split: str, count: int, requested: int) -> set[int]:
    if count <= 0:
        return set()
    target = min(count, requested)
    indices = {0, count - 1}
    counter = 0
    while len(indices) < target:
        digest = hashlib.sha256(
            b"keyai/ml-structure-probe/validator-sample/v1\0"
            + split.encode("ascii")
            + counter.to_bytes(8, "big")
        ).digest()
        indices.add(int.from_bytes(digest[:8], "big") % count)
        counter += 1
    return indices


def bit_abs_z(counts: np.ndarray, records: int) -> tuple[float, int]:
    if records <= 0:
        return (0.0, 0)
    denominator = math.sqrt(records * 0.25)
    z = np.abs((counts.astype(np.float64) - records * 0.5) / denominator)
    index = int(np.argmax(z))
    return (float(z[index]), index)


def validate(config_path: Path, manifest_path: Path) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    dataset_root = manifest_path.parent
    errors: list[str] = []

    if manifest.get("schema_version") != 1:
        errors.append("unsupported manifest schema_version")
    if manifest.get("record_size_bytes") != RECORD_SIZE:
        errors.append("unexpected record size")
    if manifest.get("config_sha256") != sha256_file(config_path):
        errors.append("config hash mismatch")

    manifest_without_hash = dict(manifest)
    recorded_manifest_hash = manifest_without_hash.pop("manifest_sha256", None)
    manifest_without_hash.pop("dataset_root_sha256", None)
    if recorded_manifest_hash != hashlib.sha256(
        canonical_json(manifest_without_hash)
    ).hexdigest():
        errors.append("manifest hash mismatch")
    if manifest.get("dataset_root_sha256") != hashlib.sha256(
        canonical_json(manifest.get("shards", []))
    ).hexdigest():
        errors.append("dataset root hash mismatch")

    seed = bytes.fromhex(config["master_seed_hex"])
    total_expected = sum(int(value) for value in config["splits"].values())
    seen_scalars: set[bytes] = set()
    scalar_bit_counts = np.zeros(256, dtype=np.int64)
    x_bit_counts = np.zeros(256, dtype=np.int64)
    y_parity_ones = 0
    residue_counts = {
        modulus: np.zeros(modulus, dtype=np.int64) for modulus in SMALL_MODULI
    }
    split_observed = {split: 0 for split in config["splits"]}
    split_samples = {
        split: sample_indices(
            split,
            int(count),
            max(2, math.ceil(int(config["validator_spot_checks"]) * int(count) / total_expected)),
        )
        for split, count in config["splits"].items()
    }
    spot_records: dict[tuple[str, int], tuple[bytes, bytes]] = {}

    for shard in manifest.get("shards", []):
        path = dataset_root / shard["relative_path"]
        if not path.is_file():
            errors.append(f"missing shard: {shard['relative_path']}")
            continue
        if sha256_file(path) != shard["sha256"]:
            errors.append(f"shard hash mismatch: {shard['relative_path']}")
            continue
        expected_bytes = int(shard["record_count"]) * RECORD_SIZE
        if path.stat().st_size != expected_bytes or int(shard["byte_count"]) != expected_bytes:
            errors.append(f"shard byte count mismatch: {shard['relative_path']}")
            continue

        raw = np.fromfile(path, dtype=np.uint8)
        records = raw.reshape((-1, RECORD_SIZE))
        scalars = records[:, :32]
        public = records[:, 32:]
        split = str(shard["split"])
        start = int(shard["start_index"])
        split_observed[split] = split_observed.get(split, 0) + len(records)

        prefixes = public[:, 0]
        if np.any((prefixes != 2) & (prefixes != 3)):
            errors.append(f"invalid compressed point prefix: {shard['relative_path']}")
        y_parity_ones += int(np.count_nonzero(prefixes == 3))
        scalar_bit_counts += np.unpackbits(scalars, axis=1, bitorder="big").sum(
            axis=0, dtype=np.int64
        )
        x_bit_counts += np.unpackbits(public[:, 1:], axis=1, bitorder="big").sum(
            axis=0, dtype=np.int64
        )

        for local_index, scalar_bytes_row in enumerate(scalars):
            scalar_bytes = scalar_bytes_row.tobytes()
            scalar = int.from_bytes(scalar_bytes, "big")
            if not 0 < scalar < N:
                errors.append(f"scalar outside [1,n-1]: {split}:{start + local_index}")
            if scalar_bytes in seen_scalars:
                errors.append(f"duplicate scalar: {split}:{start + local_index}")
            seen_scalars.add(scalar_bytes)
            for modulus in SMALL_MODULI:
                residue_counts[modulus][scalar % modulus] += 1
            global_index = start + local_index
            if global_index in split_samples.get(split, set()):
                spot_records[(split, global_index)] = (
                    scalar_bytes,
                    public[local_index].tobytes(),
                )

    observed = sum(split_observed.values())
    if observed != total_expected:
        errors.append(f"record count mismatch: expected {total_expected}, observed {observed}")
    for split, expected in config["splits"].items():
        if split_observed.get(split) != int(expected):
            errors.append(
                f"split count mismatch for {split}: "
                f"expected {expected}, observed {split_observed.get(split)}"
            )

    spot_failures: list[str] = []
    for (split, index), (scalar_bytes, compressed) in sorted(spot_records.items()):
        expected_scalar = derive_scalar(seed, split, index)
        if scalar_bytes != expected_scalar.to_bytes(32, "big"):
            spot_failures.append(f"{split}:{index}: scalar derivation mismatch")
            continue
        x, y = scalar_mul_generator(expected_scalar)
        expected_public = bytes((2 | (y & 1),)) + x.to_bytes(32, "big")
        if compressed != expected_public:
            spot_failures.append(f"{split}:{index}: independent point mismatch")
    expected_spots = sum(len(values) for values in split_samples.values())
    if len(spot_records) != expected_spots:
        errors.append(
            f"spot record coverage mismatch: expected {expected_spots}, "
            f"observed {len(spot_records)}"
        )
    errors.extend(spot_failures)

    scalar_z, scalar_bit = bit_abs_z(scalar_bit_counts, observed)
    x_z, x_bit = bit_abs_z(x_bit_counts, observed)
    parity_z = (
        abs(y_parity_ones - observed * 0.5) / math.sqrt(observed * 0.25)
        if observed
        else 0.0
    )
    thresholds = config["quality_thresholds"]
    if scalar_z > float(thresholds["max_scalar_bit_abs_z"]):
        errors.append(f"scalar bit imbalance exceeds threshold: z={scalar_z:.4f}")
    if x_z > float(thresholds["max_public_x_bit_abs_z"]):
        errors.append(f"public x bit imbalance exceeds threshold: z={x_z:.4f}")
    if parity_z > float(thresholds["max_y_parity_abs_z"]):
        errors.append(f"public y parity imbalance exceeds threshold: z={parity_z:.4f}")

    residue_summary = {}
    for modulus, counts in residue_counts.items():
        expected = observed / modulus if observed else 0.0
        max_cell_z = (
            float(np.max(np.abs(counts - expected)) / math.sqrt(expected * (1 - 1 / modulus)))
            if expected
            else 0.0
        )
        residue_summary[str(modulus)] = {
            "counts": [int(value) for value in counts],
            "max_cell_abs_z": max_cell_z,
        }

    return {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "validation_role": "data_engineering_path_and_artifact_replay",
        "source_independent": False,
        "manifest_sha256": sha256_file(manifest_path),
        "config_sha256": sha256_file(config_path),
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "records_observed": observed,
        "unique_scalars": len(seen_scalars),
        "split_records": split_observed,
        "spot_checks": {
            "requested_and_found": len(spot_records),
            "failures": spot_failures,
            "arithmetic": "pure-python Jacobian secp256k1, no producer import",
        },
        "distribution_checks": {
            "scalar_bits": {
                "max_abs_z": scalar_z,
                "argmax_bit_big_endian": scalar_bit,
                "threshold": thresholds["max_scalar_bit_abs_z"],
            },
            "public_x_bits": {
                "max_abs_z": x_z,
                "argmax_bit_big_endian": x_bit,
                "threshold": thresholds["max_public_x_bit_abs_z"],
            },
            "public_y_parity": {
                "ones": y_parity_ones,
                "max_abs_z": parity_z,
                "threshold": thresholds["max_y_parity_abs_z"],
            },
            "scalar_residues": residue_summary,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate(args.config.resolve(), args.manifest.resolve())
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
