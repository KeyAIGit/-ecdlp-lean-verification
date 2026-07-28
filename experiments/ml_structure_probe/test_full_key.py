#!/usr/bin/env python3
"""Fast unit tests for the 256-output full-key representation pipeline."""
from __future__ import annotations

import math

import numpy as np

import generate_dataset
import validate_dataset
from full_key_common import (
    FeatureStore,
    compressed_public,
    decompress_affine,
    fit_and_evaluate,
    scalar_bits,
)


G_COMPRESSED = bytes.fromhex(
    "0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798"
)


def _records(scalars: list[int]) -> np.ndarray:
    payload = b"".join(
        scalar.to_bytes(32, "big")
        + generate_dataset.compressed_public_key(scalar)
        for scalar in scalars
    )
    return np.frombuffer(payload, dtype=np.uint8).reshape((-1, 65)).copy()


def test_scalar_bits_covers_all_256_positions() -> None:
    records = np.zeros((256, 65), dtype=np.uint8)
    indices = np.arange(256)
    records[indices, indices // 8] = 1 << (7 - indices % 8)

    labels = scalar_bits(records)

    assert labels.shape == (256, 256)
    assert labels.dtype == np.uint8
    np.testing.assert_array_equal(labels, np.eye(256, dtype=np.uint8))


def test_full_public_feature_shapes() -> None:
    records = _records([1, 2, 3, generate_dataset.SECP256K1_N - 1])
    store = FeatureStore(records, workers=1)

    expected_shapes = {
        "compressed_bits_264": (4, 264),
        "compressed_bits_257": (4, 257),
        "affine_bits_512": (4, 512),
    }
    for mode, expected_shape in expected_shapes.items():
        features = store.get(mode)
        assert features.shape == expected_shape
        assert features.dtype == np.float32
        assert set(np.unique(features)).issubset({-1.0, 1.0})


def test_public_features_do_not_read_scalar_bytes() -> None:
    records = _records([1, 2, 3, 17])
    mutated = records.copy()
    mutated[:, :32] ^= np.uint8(0xA5)
    assert not np.array_equal(records[:, :32], mutated[:, :32])
    np.testing.assert_array_equal(records[:, 32:], mutated[:, 32:])

    original_store = FeatureStore(records, workers=1)
    mutated_store = FeatureStore(mutated, workers=1)
    modes = (
        "compressed_bits_264",
        "compressed_bits_257",
        "compressed_bytes",
        "x_limbs16",
        "byte_popcounts",
        "affine_bytes",
        "affine_bits_512",
        "affine_limbs16",
        "bit_interactions_16",
    )
    for mode in modes:
        np.testing.assert_array_equal(
            original_store.get(mode),
            mutated_store.get(mode),
            err_msg=f"scalar leakage into feature mode {mode}",
        )


def test_labels_do_not_read_public_bytes() -> None:
    records = _records([5, 7, 11, 13])
    mutated = records.copy()
    mutated[:, 32:] = mutated[::-1, 32:]
    assert not np.array_equal(
        compressed_public(records),
        compressed_public(mutated),
    )

    np.testing.assert_array_equal(scalar_bits(records), scalar_bits(mutated))


def test_decompresses_generator_to_known_affine_point() -> None:
    public = np.frombuffer(G_COMPRESSED, dtype=np.uint8).reshape((1, 33))
    affine = decompress_affine(public, workers=1)

    assert affine.shape == (1, 64)
    assert int.from_bytes(affine[0, :32].tobytes(), "big") == validate_dataset.GX
    assert int.from_bytes(affine[0, 32:].tobytes(), "big") == validate_dataset.GY


def test_small_256_output_fit_and_evaluate() -> None:
    seed = bytes.fromhex(
        "cfe15d25db45c654c2dcb92df85abe94c472bbbd776cfd4338687112d93a9332"
    )
    scalars = [
        generate_dataset.derive_scalar(seed, "full-key-test", index)
        for index in range(80)
    ]
    records = _records(scalars)
    train_records = records[:64]
    validation_records = records[64:]
    train_features = FeatureStore(train_records, workers=1).get(
        "compressed_bits_257"
    )
    validation_features = FeatureStore(validation_records, workers=1).get(
        "compressed_bits_257"
    )
    architecture = {
        "family": "mlp",
        "params": {
            "epochs": 1,
            "hidden_layers": [],
            "activation": "relu",
            "alpha": 1e-4,
            "batch_size": 16,
            "learning_rate_init": 1e-3,
        },
    }

    model, result = fit_and_evaluate(
        architecture,
        model_seed=19,
        train_features=train_features,
        train_labels=scalar_bits(train_records),
        validation_features=validation_features,
        validation_labels=scalar_bits(validation_records),
        jobs=1,
        prediction_batch_records=8,
        detailed=True,
    )

    probabilities = np.asarray(model.predict_proba(validation_features))
    assert probabilities.shape == (16, 256)
    assert np.isfinite(probabilities).all()
    assert result["train_records"] == 64
    assert result["validation_records"] == 16
    assert len(result["train_priors"]) == 256
    assert len(result["validation"]["per_bit"]["accuracy"]) == 256
    assert len(result["validation"]["hamming_histogram"]) == 257
    assert result["validation"]["output_bits"] == 256
    assert math.isfinite(result["validation"]["information_gain_bits_per_key"])


def main() -> int:
    test_scalar_bits_covers_all_256_positions()
    test_full_public_feature_shapes()
    test_public_features_do_not_read_scalar_bytes()
    test_labels_do_not_read_public_bytes()
    test_decompresses_generator_to_known_affine_point()
    test_small_256_output_fit_and_evaluate()
    print("FULL-KEY ML TESTS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
