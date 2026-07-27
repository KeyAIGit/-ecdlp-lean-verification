#!/usr/bin/env python3
"""Generate the deterministic prime-order j=0 toy-curve catalog."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

try:
    from .curve_math import derive_generators, search_curve
except ImportError:
    from curve_math import derive_generators, search_curve


ROOT = Path(__file__).resolve().parents[3]


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


def git_output(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.strip()


def generate(config_path: Path) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    family = config["curve_family"]
    if config["native_research_engine_outcome"] is not False:
        raise ValueError("P1E must remain outside native Research Engine outcomes")
    if max(config["field_bits"]) > 24:
        raise ValueError("the current P1E authorization is capped at 24 field bits")
    if (
        family["equation"] != "y^2=x^3+7"
        or family["curve_a"] != 0
        or family["curve_b"] != 7
    ):
        raise ValueError("P1E catalog must retain the exact secp256k1 curve shape")

    used_primes: set[int] = set()
    curves: list[dict[str, Any]] = []
    started = time.perf_counter()
    for bits in config["field_bits"]:
        for curve_index in range(int(family["curves_per_field_size"])):
            entry = search_curve(int(bits), curve_index, used_primes)
            used_primes.add(int(entry["field_p"]))
            entry["curve_index"] = curve_index
            entry["role"] = next(
                role
                for role, indices in config["curve_roles"].items()
                if curve_index in indices
            )
            entry["generators"] = derive_generators(
                entry, int(family["generators_per_curve"])
            )
            for generator_index, generator in enumerate(entry["generators"]):
                generator["generator_index"] = generator_index
                generator["role"] = next(
                    role
                    for role, indices in config["generator_roles"].items()
                    if generator_index in indices
                )
            curves.append(entry)
    arithmetic_path = Path(__file__).with_name("curve_math.py")
    result: dict[str, Any] = {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "classification": config["classification"],
        "native_research_engine_outcome": False,
        "config_sha256": sha256_file(config_path),
        "producer_sha256": sha256_file(Path(__file__)),
        "arithmetic_sha256": sha256_file(arithmetic_path),
        "source_commit": git_output("rev-parse", "HEAD"),
        "source_worktree_dirty": bool(git_output("status", "--porcelain")),
        "curve_count": len(curves),
        "field_bits": config["field_bits"],
        "curves": curves,
        "generation": {
            "wall_time_seconds": time.perf_counter() - started,
            "python": sys.version.split()[0],
            "platform": platform.platform(),
        },
    }
    result["catalog_sha256"] = hashlib.sha256(canonical_json(result)).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = generate(args.config.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        f"wrote {args.output}: {result['curve_count']} curves in "
        f"{result['generation']['wall_time_seconds']:.3f}s"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
