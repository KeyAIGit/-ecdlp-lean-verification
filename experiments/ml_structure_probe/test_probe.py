#!/usr/bin/env python3
"""Unit and end-to-end smoke tests for the ML structure-probe package."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import automl
import generate_dataset
import probe
import validate_dataset


HERE = Path(__file__).resolve().parent
G_COMPRESSED = bytes.fromhex(
    "0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798"
)


def test_known_vectors() -> None:
    assert generate_dataset.compressed_public_key(1) == G_COMPRESSED
    assert validate_dataset.scalar_mul_generator(1) == (
        validate_dataset.GX,
        validate_dataset.GY,
    )
    minus_g = generate_dataset.compressed_public_key(generate_dataset.SECP256K1_N - 1)
    assert minus_g[0] == 3
    assert minus_g[1:] == G_COMPRESSED[1:]


def test_derivation_domains() -> None:
    seed = bytes.fromhex(
        "68d843aca81dd7c92f2045925447af697caa5eaf63fa9d987c899888c7a67ea0"
    )
    train = [generate_dataset.derive_scalar(seed, "train", i) for i in range(20)]
    test = [generate_dataset.derive_scalar(seed, "test", i) for i in range(20)]
    assert len(set(train)) == len(train)
    assert set(train).isdisjoint(test)
    assert all(0 < scalar < generate_dataset.SECP256K1_N for scalar in train + test)


def test_smoke_end_to_end() -> None:
    config_path = HERE / "config" / "p0_smoke.json"
    with tempfile.TemporaryDirectory(prefix="keyai-ml-probe-") as temporary:
        output_root = Path(temporary)
        manifest_path = generate_dataset.generate(config_path, output_root)
        validation = validate_dataset.validate(config_path, manifest_path)
        assert validation["status"] == "pass", validation["errors"]
        result = probe.run_probe(config_path, manifest_path)
        assert result["pipeline_status"] == "pass"
        assert result["canaries_pass"]
        assert result["permuted_null_pass"]
        automl_result = automl.run_automl(
            HERE / "config" / "automl_smoke.json",
            manifest_path,
            output_root / "automl",
        )
        assert automl_result["pipeline_status"] == "pass"
        assert automl_result["run_summary"]["failed"] == 0
        assert len(automl_result["finalists"]) == 3
        assert not automl_result["representation_signals_requiring_replication"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest["total_records"] == 10_000
        assert manifest["total_bytes"] == 650_000


def main() -> int:
    test_known_vectors()
    test_derivation_domains()
    test_smoke_end_to_end()
    print("ML STRUCTURE PROBE TESTS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
