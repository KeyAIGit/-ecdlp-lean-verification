#!/usr/bin/env python3
"""Independent structural and arithmetic replay of P1E toy records."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[3]

try:
    from experiments.framework.ec_oracle import Curve
except ModuleNotFoundError:
    sys.path.insert(0, str(ROOT))
    from experiments.framework.ec_oracle import Curve


EXPECTED_DTYPE = np.dtype(
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


def sample_indices(count: int, requested: int, domain: bytes) -> list[int]:
    if requested <= 0 or requested >= count:
        return list(range(count))
    target = min(count, requested)
    indices = {0, count - 1} if count else set()
    counter = 0
    while len(indices) < target:
        digest = hashlib.sha256(domain + counter.to_bytes(8, "big")).digest()
        indices.add(int.from_bytes(digest[:8], "big") % count)
        counter += 1
    return sorted(indices)


def expected_unique_scalars(
    curve_id: str, order: int, count: int
) -> list[int]:
    domain = (
        f"keyai/p1-toy-record-sequence/v1/{curve_id}".encode("ascii")
        + b"/canonical-scalars"
    )
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


def weighted_groups(
    role: str, fractions: dict[str, float]
) -> list[tuple[str, int, float]]:
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


def expected_assignment_sequence(
    role: str, total: int, fractions: dict[str, float]
) -> list[tuple[str, int]]:
    groups = weighted_groups(role, fractions)
    raw = [total * weight for _, _, weight in groups]
    counts = [int(value) for value in raw]
    remaining = total - sum(counts)
    order = sorted(
        range(len(raw)),
        key=lambda index: (raw[index] - counts[index], -index),
        reverse=True,
    )
    for index in order[:remaining]:
        counts[index] += 1
    assignments: list[tuple[str, int]] = []
    for (split, generator, _), count in zip(groups, counts):
        assignments.extend([(split, generator)] * count)
    if len(assignments) != total:
        raise AssertionError("independent allocation did not fill the curve")
    return assignments


def validate(
    config_path: Path,
    catalog_path: Path,
    manifest_path: Path,
    dataset_dir: Path,
    ec_checks_per_file: int,
) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    started = time.perf_counter()
    if manifest.get("config_sha256") != sha256_file(config_path):
        errors.append("manifest config hash mismatch")
    if manifest.get("catalog_sha256") != sha256_file(catalog_path):
        errors.append("manifest catalog hash mismatch")
    if manifest.get("catalog_payload_sha256") != catalog.get(
        "catalog_sha256"
    ):
        errors.append("manifest catalog payload hash mismatch")
    if manifest.get("producer_sha256") != sha256_file(
        Path(__file__).with_name("generate_dataset.py")
    ):
        errors.append("manifest producer hash mismatch")
    if manifest.get("dtype") != [
        list(item) for item in EXPECTED_DTYPE.descr
    ]:
        errors.append("manifest dtype declaration mismatch")
    without_hash = dict(manifest)
    recorded_hash = without_hash.pop("manifest_sha256", None)
    if hashlib.sha256(canonical_json(without_hash)).hexdigest() != recorded_hash:
        errors.append("manifest payload hash mismatch")
    split_codes = {
        name: int(code) for name, code in manifest["split_codes"].items()
    }
    code_to_split = {code: name for name, code in split_codes.items()}
    blind_name = "blind_curve_blind_generator"
    catalog_index = {
        (int(entry["field_bits"]), int(entry["curve_index"])): entry
        for entry in catalog["curves"]
    }

    observed_splits = {name: 0 for name in split_codes}
    file_rows: list[dict[str, Any]] = []
    records_by_bits: dict[int, list[np.ndarray]] = {}
    files_by_bits: dict[int, list[dict[str, Any]]] = {}
    total_records = 0
    file_names: set[str] = set()
    expected_file_keys = {
        (int(bits), scope)
        for bits in config["field_bits"]
        for scope in ("development", "blind")
    }
    actual_file_keys = {
        (int(entry.get("field_bits", -1)), entry.get("scope"))
        for entry in manifest["files"]
    }
    if (
        actual_file_keys != expected_file_keys
        or len(manifest["files"]) != len(expected_file_keys)
    ):
        errors.append("manifest shard identity set mismatch")
    for file_entry in manifest["files"]:
        bits = int(file_entry["field_bits"])
        if bits not in {int(value) for value in config["field_bits"]}:
            errors.append(f"unauthorized field width in {file_entry['relative_path']}")
        scope = file_entry.get("scope")
        relative_path = str(file_entry["relative_path"])
        if relative_path in file_names:
            errors.append(f"duplicate manifest data path: {relative_path}")
            continue
        file_names.add(relative_path)
        if scope not in {"development", "blind"}:
            errors.append(f"invalid shard scope: {relative_path}")
        path = dataset_dir / relative_path
        if not path.is_file():
            errors.append(f"missing data file: {relative_path}")
            continue
        if sha256_file(path) != file_entry["sha256"]:
            errors.append(f"data hash mismatch: {relative_path}")
            continue
        records = np.load(path, mmap_mode="r", allow_pickle=False)
        if records.dtype != EXPECTED_DTYPE:
            errors.append(f"record dtype mismatch: {relative_path}")
            continue
        if len(records) != int(file_entry["records"]):
            errors.append(f"record count mismatch: {relative_path}")
        observed_file_splits = {
            name: int(np.count_nonzero(records["split_code"] == code))
            for name, code in split_codes.items()
        }
        if observed_file_splits != {
            name: int(count)
            for name, count in file_entry["split_counts"].items()
        }:
            errors.append(f"per-file split counts mismatch: {relative_path}")
        unknown_codes = set(
            int(value) for value in np.unique(records["split_code"])
        ) - set(code_to_split)
        if unknown_codes:
            errors.append(f"unknown split codes in {relative_path}")
        present_splits = {
            name for name, count in observed_file_splits.items() if count
        }
        if scope == "development" and blind_name in present_splits:
            errors.append(f"development shard contains blind rows: {relative_path}")
        if scope == "blind" and present_splits != {blind_name}:
            errors.append(f"blind shard boundary failure: {relative_path}")
        if np.any(records["scalar"] == 0) or np.any(
            records["scalar"] >= records["group_order"]
        ):
            errors.append(f"scalar range failure: {relative_path}")
        for name, count in observed_file_splits.items():
            observed_splits[name] += count
        records_by_bits.setdefault(bits, []).append(np.asarray(records))
        files_by_bits.setdefault(bits, []).append(file_entry)
        total_records += len(records)
        file_rows.append(
            {
                "field_bits": bits,
                "scope": scope,
                "path": relative_path,
                "records": len(records),
                "sha256": file_entry["sha256"],
                "split_counts": observed_file_splits,
                "ec_checks": 0,
            }
        )

    if total_records != int(manifest["records"]):
        errors.append("total record count mismatch")
    if total_records > int(config["budget"]["max_total_records"]):
        errors.append("record budget exceeded")
    if observed_splits != {
        name: int(value) for name, value in manifest["split_counts"].items()
    }:
        errors.append("aggregate split counts mismatch")

    unique_q_checks = []
    allocation_checks = []
    ec_failures: list[str] = []
    total_ec_checks = 0
    for bits in config["field_bits"]:
        bits = int(bits)
        size_files = files_by_bits.get(bits, [])
        scopes = [entry.get("scope") for entry in size_files]
        if sorted(scopes) != ["blind", "development"]:
            errors.append(f"{bits}-bit shards are not exactly development+blind")
        matrices = records_by_bits.get(bits, [])
        if not matrices:
            errors.append(f"no records for {bits} bits")
            continue
        records = np.concatenate(matrices)
        if np.any(records["field_p"] < (1 << (bits - 1))) or np.any(
            records["field_p"] >= (1 << bits)
        ):
            errors.append(f"{bits}-bit field width mismatch")
        expected_curve_indices = {
            curve_index
            for field_bits, curve_index in catalog_index
            if field_bits == bits
        }
        observed_curve_indices = {
            int(value) for value in np.unique(records["curve_index"])
        }
        if observed_curve_indices != expected_curve_indices:
            errors.append(f"{bits}-bit catalog curve coverage mismatch")

        for curve_index in sorted(observed_curve_indices):
            subset = records[records["curve_index"] == curve_index]
            entry = catalog_index[(bits, curve_index)]
            prime = int(entry["field_p"])
            order = int(entry["group_order"])
            expected_count = min(
                int(config["records_per_curve_cap"][str(bits)]), order - 1
            )
            if len(subset) != expected_count:
                errors.append(
                    f"b{bits}/c{curve_index}: record cap mismatch"
                )
            for field, expected in (
                ("field_p", prime),
                ("group_order", order),
                ("curve_a", 0),
                ("curve_b", 7),
                ("beta", int(entry["glv"]["beta"])),
                ("lambda", int(entry["glv"]["lambda"])),
            ):
                if np.any(subset[field] != expected):
                    errors.append(
                        f"b{bits}/c{curve_index}: inconsistent {field}"
                    )
            qx = subset["qx"].astype(np.uint64)
            qy = subset["qy"].astype(np.uint64)
            p64 = np.uint64(prime)
            rhs = ((qx * qx % p64) * qx + np.uint64(7)) % p64
            if np.any(qy * qy % p64 != rhs):
                errors.append(f"b{bits}/c{curve_index}: off-curve Q")
            packed = (qx << np.uint64(32)) | qy
            unique_count = len(np.unique(packed))
            if unique_count != len(subset):
                errors.append(f"b{bits}/c{curve_index}: repeated physical Q")
            unique_q_checks.append(
                {
                    "field_bits": bits,
                    "curve_index": curve_index,
                    "records": len(subset),
                    "unique_q": unique_count,
                }
            )

            generators = entry["generators"]
            if np.any(subset["generator_index"] >= len(generators)):
                errors.append(f"b{bits}/c{curve_index}: unknown generator")
                continue
            generator_points = [
                (int(item["point"][0]), int(item["point"][1]))
                for item in generators
            ]
            for generator_index, generator_point in enumerate(generator_points):
                generator_subset = subset[
                    subset["generator_index"] == generator_index
                ]
                if len(generator_subset) and (
                    np.any(generator_subset["gx"] != generator_point[0])
                    or np.any(generator_subset["gy"] != generator_point[1])
                ):
                    errors.append(
                        f"b{bits}/c{curve_index}/g{generator_index}: "
                        "generator mapping mismatch"
                    )

            canonical_sequence = expected_unique_scalars(
                entry["id"], order, expected_count
            )
            assignment_sequence = expected_assignment_sequence(
                entry["role"], expected_count, config["split_fractions"]
            )
            expected_by_scalar = {
                canonical_scalar: assignment
                for canonical_scalar, assignment in zip(
                    canonical_sequence, assignment_sequence
                )
            }
            observed_canonical: set[int] = set()
            allocation_failures = 0
            for row in subset:
                generator_index = int(row["generator_index"])
                multiplier = int(
                    generators[generator_index]["base_multiplier"]
                )
                canonical_scalar = int(row["scalar"]) * multiplier % order
                observed_canonical.add(canonical_scalar)
                actual_split = code_to_split.get(int(row["split_code"]))
                expected_assignment = expected_by_scalar.get(canonical_scalar)
                if expected_assignment != (actual_split, generator_index):
                    allocation_failures += 1
            if observed_canonical != set(canonical_sequence):
                errors.append(
                    f"b{bits}/c{curve_index}: canonical scalar sample mismatch"
                )
            if allocation_failures:
                errors.append(
                    f"b{bits}/c{curve_index}: {allocation_failures} exact "
                    "scalar-to-split allocations differ"
                )
            allocation_checks.append(
                {
                    "field_bits": bits,
                    "curve_index": curve_index,
                    "records": len(subset),
                    "allocation_failures": allocation_failures,
                }
            )

            indices = sample_indices(
                len(subset),
                ec_checks_per_file,
                f"keyai/p1-validator/b{bits}/c{curve_index}".encode("ascii"),
            )
            curve = Curve(prime, 0, 7)
            for index in indices:
                row = subset[index]
                generator = (int(row["gx"]), int(row["gy"]))
                target = (int(row["qx"]), int(row["qy"]))
                if curve.scalar_mul(int(row["scalar"]), generator) != target:
                    ec_failures.append(
                        f"b{bits}/c{curve_index}:{index}: [d]G != Q"
                    )
            total_ec_checks += len(indices)
            matching_file_rows = [
                item for item in file_rows if item["field_bits"] == bits
            ]
            if matching_file_rows:
                share = len(indices) // len(matching_file_rows)
                for item in matching_file_rows:
                    item["ec_checks"] += share
                matching_file_rows[0]["ec_checks"] += (
                    len(indices) - share * len(matching_file_rows)
                )

    errors.extend(ec_failures)
    return {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "validation_role": (
            "independent shard-boundary, exact allocation, and EC replay"
        ),
        "producer_imported": False,
        "validator_sha256": sha256_file(Path(__file__)),
        "oracle_sha256": sha256_file(
            ROOT / "experiments" / "framework" / "ec_oracle.py"
        ),
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "manifest_sha256": sha256_file(manifest_path),
        "records": total_records,
        "split_counts": observed_splits,
        "unique_q_checks": unique_q_checks,
        "allocation_checks": allocation_checks,
        "ec_check_failures": ec_failures,
        "ec_checks": total_ec_checks,
        "full_ec_replay": ec_checks_per_file <= 0,
        "files": sorted(
            file_rows, key=lambda row: (row["field_bits"], row["scope"])
        ),
        "wall_time_seconds": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dataset-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--ec-checks-per-curve",
        type=int,
        default=0,
        help="0 verifies every record; a positive value requests a bounded sample",
    )
    args = parser.parse_args()
    result = validate(
        args.config.resolve(),
        args.catalog.resolve(),
        args.manifest.resolve(),
        args.dataset_dir.resolve(),
        args.ec_checks_per_curve,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        f"dataset validation {result['status']}: {result['records']} records, "
        f"{result['ec_checks']} independent EC checks"
    )
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
