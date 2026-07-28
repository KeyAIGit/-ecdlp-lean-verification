#!/usr/bin/env python3
"""Generate leakage-resistant P1E toy-curve records."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .curve_math import Curve, derive_integer
except ImportError:
    from curve_math import Curve, derive_integer


DTYPE = np.dtype(
    [
        ("field_p", "<u4"),
        ("group_order", "<u4"),
        ("curve_a", "<u4"),
        ("curve_b", "<u4"),
        ("beta", "<u4"),
        ("lambda", "<u4"),
        ("gx", "<u4"),
        ("gy", "<u4"),
        ("qx", "<u4"),
        ("qy", "<u4"),
        ("scalar", "<u4"),
        ("curve_index", "u1"),
        ("generator_index", "u1"),
        ("split_code", "u1"),
    ]
)

SPLITS = {
    "train": 0,
    "seen_curve_seen_generator": 1,
    "seen_curve_new_generator": 2,
    "new_curve_seen_generator": 3,
    "new_curve_new_generator": 4,
    "blind_curve_blind_generator": 5,
}


def canonical_json(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def allocate(
    total: int, weighted_groups: list[tuple[str, int, float]]
) -> list[tuple[str, int, int]]:
    raw = [total * weight for _, _, weight in weighted_groups]
    counts = [int(value) for value in raw]
    remaining = total - sum(counts)
    order = sorted(
        range(len(raw)),
        key=lambda index: (raw[index] - counts[index], -index),
        reverse=True,
    )
    for index in order[:remaining]:
        counts[index] += 1
    return [
        (split, generator, count)
        for (split, generator, _), count in zip(weighted_groups, counts)
        if count
    ]


def curve_plan(role: str, fractions: dict[str, float]) -> list[tuple[str, int, float]]:
    if role == "train":
        return [
            ("train", generator, fractions["train_curve_train_generator"] / 3)
            for generator in (0, 1, 2)
        ] + [
            (
                "seen_curve_seen_generator",
                generator,
                fractions["seen_curve_seen_generator"] / 3,
            )
            for generator in (0, 1, 2)
        ] + [
            (
                "seen_curve_new_generator",
                3,
                fractions["seen_curve_new_generator"],
            )
        ]
    if role == "development":
        return [
            (
                "new_curve_seen_generator",
                generator,
                fractions["new_curve_seen_generator"] / 3,
            )
            for generator in (0, 1, 2)
        ] + [
            (
                "new_curve_new_generator",
                3,
                fractions["new_curve_new_generator"],
            )
        ]
    if role == "blind":
        return [
            (
                "blind_curve_blind_generator",
                generator,
                fractions["blind_curve_blind_generator"] / 2,
            )
            for generator in (4, 5)
        ]
    raise ValueError(f"unknown curve role: {role}")


def unique_rejection_scalars(
    domain: bytes, order: int, count: int
) -> list[int]:
    """Draw unique scalars uniformly without modulo bias or interval structure."""
    modulus = order - 1
    sample_space = 1 << 256
    acceptance_limit = sample_space - sample_space % modulus
    output: list[int] = []
    seen: set[int] = set()
    counter = 0
    while len(output) < count:
        candidate = int.from_bytes(
            hashlib.sha256(domain + counter.to_bytes(8, "big")).digest(),
            "big",
        )
        counter += 1
        if candidate >= acceptance_limit:
            continue
        scalar = 1 + candidate % modulus
        if scalar in seen:
            continue
        seen.add(scalar)
        output.append(scalar)
    return output


def generate_curve_rows(
    entry: dict[str, Any], config: dict[str, Any]
) -> tuple[np.ndarray, dict[str, int]]:
    bits = int(entry["field_bits"])
    prime, order = int(entry["field_p"]), int(entry["group_order"])
    cap = min(int(config["records_per_curve_cap"][str(bits)]), order - 1)
    plan = allocate(cap, curve_plan(entry["role"], config["split_fractions"]))
    curve = Curve(prime, int(entry["curve_a"]), int(entry["curve_b"]))
    base_raw = entry["base_point"]
    base = (int(base_raw[0]), int(base_raw[1]))
    domain = f"keyai/p1-toy-record-sequence/v1/{entry['id']}".encode("ascii")
    canonical_scalars = unique_rejection_scalars(
        domain + b"/canonical-scalars", order, cap
    )
    rows = np.empty(cap, dtype=DTYPE)
    cursor = 0
    split_counts: dict[str, int] = {}
    generators = entry["generators"]
    for split, generator_index, count in plan:
        generator = generators[generator_index]
        generator_point = (
            int(generator["point"][0]),
            int(generator["point"][1]),
        )
        inverse_multiplier = pow(int(generator["base_multiplier"]), -1, order)
        for _ in range(count):
            canonical_scalar = canonical_scalars[cursor]
            point = curve.scalar_mul(canonical_scalar, base)
            if point is None:
                raise AssertionError("nonzero canonical scalar reached infinity")
            scalar = canonical_scalar * inverse_multiplier % order
            if scalar == 0:
                raise AssertionError("zero scalar generated")
            rows[cursor] = (
                prime,
                order,
                int(entry["curve_a"]),
                int(entry["curve_b"]),
                int(entry["glv"]["beta"]),
                int(entry["glv"]["lambda"]),
                generator_point[0],
                generator_point[1],
                point[0],
                point[1],
                scalar,
                int(entry["curve_index"]),
                generator_index,
                SPLITS[split],
            )
            cursor += 1
        split_counts[split] = split_counts.get(split, 0) + count
    if cursor != cap:
        raise AssertionError("curve plan did not fill the record cap")
    shuffle_seed = derive_integer(domain + b"/shuffle", 1 << 63)
    np.random.default_rng(shuffle_seed).shuffle(rows)
    return rows, split_counts


def generate(
    config_path: Path, catalog_path: Path, output_dir: Path
) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    if catalog["config_sha256"] != sha256_file(config_path):
        raise ValueError("catalog/config binding mismatch")
    output_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    files = []
    total_records = 0
    aggregate_splits = {name: 0 for name in SPLITS}
    for bits in config["field_bits"]:
        selected = [
            entry for entry in catalog["curves"] if entry["field_bits"] == bits
        ]
        matrices = []
        split_counts = {name: 0 for name in SPLITS}
        for entry in selected:
            rows, counts = generate_curve_rows(entry, config)
            matrices.append(rows)
            for name, count in counts.items():
                split_counts[name] += count
                aggregate_splits[name] += count
        records = np.concatenate(matrices)
        scopes = {
            "development": records[
                records["split_code"]
                != np.uint8(SPLITS["blind_curve_blind_generator"])
            ],
            "blind": records[
                records["split_code"]
                == np.uint8(SPLITS["blind_curve_blind_generator"])
            ],
        }
        for scope, scoped_records in scopes.items():
            path = output_dir / f"toy_records_b{bits}_{scope}.npy"
            np.save(path, scoped_records, allow_pickle=False)
            digest = sha256_file(path)
            scoped_counts = {
                name: int(
                    np.count_nonzero(scoped_records["split_code"] == code)
                )
                for name, code in SPLITS.items()
            }
            files.append(
                {
                    "field_bits": bits,
                    "scope": scope,
                    "relative_path": path.name,
                    "records": len(scoped_records),
                    "bytes": path.stat().st_size,
                    "sha256": digest,
                    "split_counts": scoped_counts,
                }
            )
        total_records += len(records)
    if total_records > int(config["budget"]["max_total_records"]):
        raise RuntimeError("dataset exceeds preregistered record budget")
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "classification": config["classification"],
        "dtype": DTYPE.descr,
        "split_codes": SPLITS,
        "config_sha256": sha256_file(config_path),
        "catalog_sha256": sha256_file(catalog_path),
        "catalog_payload_sha256": catalog["catalog_sha256"],
        "producer_sha256": sha256_file(Path(__file__)),
        "records": total_records,
        "split_counts": aggregate_splits,
        "files": files,
        "generation": {
            "wall_time_seconds": time.perf_counter() - started,
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
    }
    manifest["manifest_sha256"] = hashlib.sha256(canonical_json(manifest)).hexdigest()
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    manifest = generate(
        args.config.resolve(), args.catalog.resolve(), args.output_dir.resolve()
    )
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        f"wrote {manifest['records']} records in "
        f"{manifest['generation']['wall_time_seconds']:.3f}s"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
