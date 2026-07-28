#!/usr/bin/env python3
"""Independently validate the P1E catalog and exact point counts."""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]

try:
    from experiments.framework.ec_oracle import Curve, is_prime
except ModuleNotFoundError:
    sys.path.insert(0, str(ROOT))
    from experiments.framework.ec_oracle import Curve, is_prime


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


def exact_point_count(prime: int) -> tuple[int, float]:
    started = time.perf_counter()
    exponent = (prime - 1) // 2
    count = 1
    for x in range(prime):
        rhs = (x * x * x + 7) % prime
        if rhs == 0:
            count += 1
        elif pow(rhs, exponent, prime) == 1:
            count += 2
    return count, time.perf_counter() - started


def prime_factors(value: int) -> list[int]:
    factors: list[int] = []
    remainder = value
    divisor = 2
    while divisor * divisor <= remainder:
        if remainder % divisor == 0:
            factors.append(divisor)
            while remainder % divisor == 0:
                remainder //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if remainder > 1:
        factors.append(remainder)
    return factors


def multiplicative_order(value: int, prime: int) -> int:
    order = prime - 1
    for factor in prime_factors(order):
        while order % factor == 0 and pow(value, order // factor, prime) == 1:
            order //= factor
    return order


def validate_entry(
    entry: dict[str, Any], exact_count: int, count_seconds: float
) -> dict[str, Any]:
    errors: list[str] = []
    prime = int(entry["field_p"])
    order = int(entry["group_order"])
    bits = int(entry["field_bits"])
    if not is_prime(prime):
        errors.append("field_p is not prime")
    if not is_prime(order):
        errors.append("group_order is not prime")
    if prime.bit_length() != bits or order.bit_length() != bits:
        errors.append("field or group order has the wrong bit width")
    if prime % 12 != 7:
        errors.append("field prime is not 7 modulo 12")
    if int(entry.get("curve_a", -1)) != 0 or int(
        entry.get("curve_b", -1)
    ) != 7:
        errors.append("curve equation is not y^2=x^3+7")
    if order == prime or entry.get("anomalous") is not False:
        errors.append("anomalous curve is forbidden")
    if exact_count != order:
        errors.append(f"exact point count {exact_count} differs from order {order}")
    bound = math.isqrt(4 * prime)
    lower, upper = prime + 1 - bound, prime + 1 + bound
    if not lower <= order <= upper:
        errors.append("group order violates the Hasse interval")
    if 2 * order <= upper:
        errors.append("Hasse divisibility certificate is not unique")
    if int(entry["cofactor"]) != 1:
        errors.append("cofactor must be one")
    embedding_degree = multiplicative_order(prime, order)
    if embedding_degree != int(entry["embedding_degree"]):
        errors.append("embedding degree mismatch")
    if embedding_degree <= 100:
        errors.append("embedding degree is too small")

    curve = Curve(prime, int(entry["curve_a"]), int(entry["curve_b"]))
    base_raw = entry["base_point"]
    base = (int(base_raw[0]), int(base_raw[1]))
    if not curve.is_on_curve(base):
        errors.append("base point is off curve")
    if curve.scalar_mul(order, base) is not None:
        errors.append("group order does not annihilate base point")
    glv = entry["glv"]
    beta, eigenvalue = int(glv["beta"]), int(glv["lambda"])
    if (beta * beta + beta + 1) % prime != 0:
        errors.append("beta polynomial check failed")
    if (eigenvalue * eigenvalue + eigenvalue + 1) % order != 0:
        errors.append("lambda polynomial check failed")
    image = (beta * base[0] % prime, base[1])
    if curve.scalar_mul(eigenvalue, base) != image:
        errors.append("GLV eigenpair check failed")

    seen_points: set[tuple[int, int]] = set()
    seen_orbits: set[int] = set()
    if len(entry.get("generators", [])) != 6:
        errors.append("curve does not have exactly six generators")
    for generator_index, generator in enumerate(entry.get("generators", [])):
        point_raw = generator["point"]
        point = (int(point_raw[0]), int(point_raw[1]))
        multiplier = int(generator["base_multiplier"])
        if not 1 <= multiplier < order:
            errors.append(f"generator multiplier out of range: {generator['id']}")
        if generator.get("generator_index") != generator_index:
            errors.append(f"generator index mismatch: {generator['id']}")
        if generator.get("id") != f"{entry['id']}-g{generator_index}":
            errors.append(f"generator id mismatch: {generator['id']}")
        if point in seen_points:
            errors.append(f"duplicate generator point: {generator['id']}")
        seen_points.add(point)
        if curve.scalar_mul(multiplier, base) != point:
            errors.append(f"generator multiplier mismatch: {generator['id']}")
        if curve.scalar_mul(order, point) is not None:
            errors.append(f"generator has wrong order: {generator['id']}")
        orbit: set[int] = set()
        current = multiplier % order
        for _ in range(3):
            orbit.add(current)
            orbit.add((-current) % order)
            current = current * eigenvalue % order
        if orbit & seen_orbits:
            errors.append(f"generator GLV orbit reused: {generator['id']}")
        seen_orbits.update(orbit)
    return {
        "curve_id": entry["id"],
        "field_bits": bits,
        "field_p": prime,
        "group_order": order,
        "exact_point_count": exact_count,
        "point_count_seconds": count_seconds,
        "embedding_degree": embedding_degree,
        "status": "pass" if not errors else "fail",
        "errors": errors,
    }


def validate(
    config_path: Path, catalog_path: Path, workers: int
) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if catalog.get("experiment_id") != config.get("experiment_id"):
        errors.append("catalog experiment id mismatch")
    if catalog.get("config_sha256") != sha256_file(config_path):
        errors.append("catalog config hash mismatch")
    if catalog.get("catalog_nonce") != config["curve_family"].get(
        "catalog_nonce"
    ):
        errors.append("catalog nonce mismatch")
    retired_field_primes = sorted(
        int(value)
        for value in config["curve_family"].get("retired_field_primes", [])
    )
    retired_field_prime_set = set(retired_field_primes)
    retired_sha256 = hashlib.sha256(
        canonical_json(retired_field_primes)
    ).hexdigest()
    if (
        catalog.get("retired_field_prime_count")
        != len(retired_field_primes)
        or catalog.get("retired_field_primes_sha256") != retired_sha256
        or config["curve_family"].get("retired_field_primes_sha256")
        != retired_sha256
    ):
        errors.append("retired field-prime binding mismatch")
    if catalog.get("source_worktree_dirty") is not False:
        errors.append("catalog source tree was dirty")
    package_dir = Path(__file__).resolve().parent
    if catalog.get("producer_sha256") != sha256_file(
        package_dir / "generate_curves.py"
    ):
        errors.append("catalog producer hash mismatch")
    if catalog.get("arithmetic_sha256") != sha256_file(
        package_dir / "curve_math.py"
    ):
        errors.append("catalog arithmetic hash mismatch")
    without_hash = dict(catalog)
    recorded_hash = without_hash.pop("catalog_sha256", None)
    computed_hash = hashlib.sha256(canonical_json(without_hash)).hexdigest()
    if recorded_hash != computed_hash:
        errors.append("catalog hash mismatch")
    expected_count = (
        len(config["field_bits"])
        * int(config["curve_family"]["curves_per_field_size"])
    )
    if catalog.get("curve_count") != expected_count:
        errors.append("catalog curve count mismatch")

    entries = catalog.get("curves", [])
    if len(entries) != expected_count:
        errors.append("actual catalog entry count mismatch")
    if any(
        int(entry.get("field_p", -1)) in retired_field_prime_set
        for entry in entries
    ):
        errors.append("catalog reuses a retired field prime")
    allowed_field_bits = {int(value) for value in config["field_bits"]}
    if any(
        int(entry.get("field_bits", -1)) not in allowed_field_bits
        for entry in entries
    ):
        errors.append("catalog contains an unauthorized field width")
    curve_ids = [entry.get("id") for entry in entries]
    field_primes = [int(entry.get("field_p", 0)) for entry in entries]
    if len(set(curve_ids)) != len(curve_ids):
        errors.append("catalog curve IDs are not unique")
    if len(set(field_primes)) != len(field_primes):
        errors.append("catalog field primes are not unique")
    expected_indices = set(
        range(int(config["curve_family"]["curves_per_field_size"]))
    )
    for bits in config["field_bits"]:
        size_entries = [
            entry for entry in entries if int(entry.get("field_bits", -1)) == bits
        ]
        if len(size_entries) != int(
            config["curve_family"]["curves_per_field_size"]
        ):
            errors.append(f"{bits}-bit catalog entry count mismatch")
        entry_keys = {
            (int(entry.get("field_bits", -1)), int(entry.get("curve_index", -1)))
            for entry in size_entries
        }
        if len(entry_keys) != len(size_entries):
            errors.append(f"{bits}-bit catalog curve keys are not unique")
        observed_indices = {
            int(entry.get("curve_index", -1)) for entry in size_entries
        }
        if observed_indices != expected_indices:
            errors.append(f"{bits}-bit catalog curve indices mismatch")
        for entry in size_entries:
            curve_index = int(entry.get("curve_index", -1))
            expected_role = next(
                (
                    role
                    for role, indices in config["curve_roles"].items()
                    if curve_index in indices
                ),
                None,
            )
            if entry.get("role") != expected_role:
                errors.append(f"{entry.get('id')}: curve role mismatch")
            generators = entry.get("generators", [])
            if len(generators) != int(
                config["curve_family"]["generators_per_curve"]
            ):
                errors.append(f"{entry.get('id')}: generator count mismatch")
            for generator_index, generator in enumerate(generators):
                expected_generator_role = next(
                    (
                        role
                        for role, indices in config[
                            "generator_roles"
                        ].items()
                        if generator_index in indices
                    ),
                    None,
                )
                if generator.get("role") != expected_generator_role:
                    errors.append(
                        f"{entry.get('id')}: generator role mismatch at "
                        f"{generator_index}"
                    )
    started = time.perf_counter()
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(exact_point_count, int(entry["field_p"])): entry
            for entry in entries
        }
        rows = []
        for future in concurrent.futures.as_completed(futures):
            entry = futures[future]
            count, seconds = future.result()
            rows.append(validate_entry(entry, count, seconds))
    rows.sort(key=lambda row: (row["field_bits"], row["curve_id"]))
    for row in rows:
        errors.extend(f"{row['curve_id']}: {error}" for error in row["errors"])
    return {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "validation_role": "independent exact toy-curve catalog replay",
        "producer_imported": False,
        "validator_sha256": sha256_file(Path(__file__)),
        "oracle_sha256": sha256_file(
            ROOT / "experiments" / "framework" / "ec_oracle.py"
        ),
        "catalog_sha256": sha256_file(catalog_path),
        "catalog_payload_sha256": recorded_hash,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "curve_count": len(rows),
        "wall_time_seconds": time.perf_counter() - started,
        "curves": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    result = validate(
        args.config.resolve(), args.catalog.resolve(), max(1, args.workers)
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        f"catalog validation {result['status']}: {result['curve_count']} curves "
        f"in {result['wall_time_seconds']:.3f}s"
    )
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
