#!/usr/bin/env python3
"""Fast unit tests for the P1 toy-curve scaling package."""
from __future__ import annotations

import copy
import json
import math
import warnings
from functools import lru_cache
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

try:
    from .curve_math import (
        Curve,
        candidate_orders_from_hasse_bsgs,
        derive_generators,
        is_prime,
        prime_order_certificate,
        search_curve,
    )
    from .generate_dataset import SPLITS, generate_curve_rows
    from .representations import (
        FeatureStore,
        public_fingerprint,
        scalar_bits,
    )
    from .run_assay import (
        bsgs_solve,
        build_model,
        exclusive_output_lock,
        finalize_success_ledger,
        pollard_rho_solve,
        predict_probabilities,
        public_uniform_scalar_prior,
    )
except ImportError:
    from curve_math import (
        Curve,
        candidate_orders_from_hasse_bsgs,
        derive_generators,
        is_prime,
        prime_order_certificate,
        search_curve,
    )
    from generate_dataset import SPLITS, generate_curve_rows
    from representations import FeatureStore, public_fingerprint, scalar_bits
    from run_assay import (
        bsgs_solve,
        build_model,
        exclusive_output_lock,
        finalize_success_ledger,
        pollard_rho_solve,
        predict_probabilities,
        public_uniform_scalar_prior,
    )


HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config" / "p1_toy_scaling.json"
FEATURE_MODES = (
    "compressed_relation_bits",
    "affine_relation_bits",
    "compressed_relation_glv_bits",
    "mismatched_relation_bits",
    "opaque_relation_bits",
    "curve_generator_only_bits",
)


@lru_cache(maxsize=1)
def _catalog_nonce() -> str:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return str(config["curve_family"]["catalog_nonce"])


@lru_cache(maxsize=1)
def _base_entry() -> dict[str, object]:
    entry = search_curve(13, 0, set(), _catalog_nonce())
    entry["curve_index"] = 0
    entry["role"] = "train"
    entry["generators"] = derive_generators(entry, 6)
    return entry


def _entry() -> dict[str, object]:
    return copy.deepcopy(_base_entry())


@lru_cache(maxsize=1)
def _train_rows() -> np.ndarray:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    rows, _ = generate_curve_rows(_entry(), config)
    return rows


def _exact_point_count(prime: int) -> int:
    exponent = (prime - 1) // 2
    count = 1
    for x in range(prime):
        rhs = (pow(x, 3, prime) + 7) % prime
        if rhs == 0:
            count += 1
        elif pow(rhs, exponent, prime) == 1:
            count += 2
    return count


def _point_set(records: np.ndarray) -> set[tuple[int, int]]:
    return {
        (int(row["qx"]), int(row["qy"]))
        for row in records
    }


def test_curve_order_and_hasse_certificate() -> None:
    first = _entry()
    replay = search_curve(13, 0, set(), _catalog_nonce())
    assert first["field_p"] == replay["field_p"]
    assert first["group_order"] == replay["group_order"]
    assert first["base_point"] == replay["base_point"]

    prime = int(first["field_p"])
    order = int(first["group_order"])
    base_raw = first["base_point"]
    base = (int(base_raw[0]), int(base_raw[1]))
    curve = Curve(prime, 0, 7)

    assert prime.bit_length() == 13
    assert order.bit_length() == 13
    assert prime % 12 == 7
    assert is_prime(prime)
    assert is_prime(order)
    assert order != prime
    assert int(first["cofactor"]) == 1
    assert int(first["embedding_degree"]) > 100
    assert curve.is_on_curve(base)
    assert curve.scalar_mul(order, base) is None
    assert curve.scalar_mul(order - 1, base) == curve.negate(base)
    assert _exact_point_count(prime) == order

    candidates = candidate_orders_from_hasse_bsgs(curve, base)
    assert order in candidates
    assert prime_order_certificate(curve, base) == order
    lower = prime + 1 - math.isqrt(4 * prime)
    upper = prime + 1 + math.isqrt(4 * prime)
    assert lower <= order <= upper
    assert 2 * order > upper


def test_glv_and_generator_orbits() -> None:
    entry = _entry()
    prime = int(entry["field_p"])
    order = int(entry["group_order"])
    curve = Curve(prime, 0, 7)
    base_raw = entry["base_point"]
    base = (int(base_raw[0]), int(base_raw[1]))
    glv = entry["glv"]
    beta = int(glv["beta"])
    eigenvalue = int(glv["lambda"])

    assert (beta * beta + beta + 1) % prime == 0
    assert (eigenvalue * eigenvalue + eigenvalue + 1) % order == 0
    assert pow(beta, 3, prime) == 1 and beta != 1
    assert pow(eigenvalue, 3, order) == 1 and eigenvalue != 1
    assert curve.scalar_mul(eigenvalue, base) == (
        beta * base[0] % prime,
        base[1],
    )

    seen_points: set[tuple[int, int]] = set()
    seen_multiplier_orbits: set[int] = set()
    for generator in entry["generators"]:
        raw = generator["point"]
        point = (int(raw[0]), int(raw[1]))
        multiplier = int(generator["base_multiplier"])
        assert point not in seen_points
        assert curve.is_on_curve(point)
        assert curve.scalar_mul(multiplier, base) == point
        assert curve.scalar_mul(order, point) is None
        assert curve.scalar_mul(eigenvalue, point) == (
            beta * point[0] % prime,
            point[1],
        )

        orbit: set[int] = set()
        current = multiplier % order
        for _ in range(3):
            orbit.add(current)
            orbit.add((-current) % order)
            current = current * eigenvalue % order
        assert len(orbit) == 6
        assert orbit.isdisjoint(seen_multiplier_orbits)
        seen_points.add(point)
        seen_multiplier_orbits.update(orbit)


def test_public_features_never_read_scalar() -> None:
    all_records = _train_rows()
    records = all_records[all_records["generator_index"] == 0][:16].copy()
    assert len(records) == 16
    mutated = records.copy()
    orders = mutated["group_order"].astype(np.uint64)
    replacement = mutated["scalar"].astype(np.uint64) % (orders - 1) + 1
    mutated["scalar"] = replacement.astype(mutated["scalar"].dtype)

    original_labels = scalar_bits(records, 13)
    mutated_labels = scalar_bits(mutated, 13)
    assert np.all(np.any(original_labels != mutated_labels, axis=1))
    assert public_fingerprint(records) == public_fingerprint(mutated)

    original_store = FeatureStore(records, 13)
    mutated_store = FeatureStore(mutated, 13)
    expected_columns = {
        "compressed_relation_bits": 54,
        "affine_relation_bits": 78,
        "compressed_relation_glv_bits": 80,
        "mismatched_relation_bits": 54,
        "opaque_relation_bits": 154,
        "curve_generator_only_bits": 40,
    }
    for mode in FEATURE_MODES:
        original = original_store.get(mode)
        changed = mutated_store.get(mode)
        assert original.shape == (len(records), expected_columns[mode])
        assert original.dtype == np.float32
        assert set(np.unique(original)).issubset({-1.0, 1.0})
        np.testing.assert_array_equal(
            original,
            changed,
            err_msg=f"scalar leaked into public feature mode {mode}",
        )
        if mode == "opaque_relation_bits":
            np.testing.assert_array_equal(original, original_store.get(mode))

    assert not np.array_equal(
        original_store.get("compressed_relation_bits", leaked_bits=13),
        mutated_store.get("compressed_relation_bits", leaked_bits=13),
    )


def test_mismatched_relation_rotates_q_and_preserves_marginals() -> None:
    all_records = _train_rows()
    records = all_records[all_records["generator_index"] == 0][:32].copy()
    assert len(records) == 32
    store = FeatureStore(records, 13)
    matched = store.get("compressed_relation_bits")
    mismatched = store.get("mismatched_relation_bits")

    q_start = 13 + 13 + 14
    np.testing.assert_array_equal(matched[:, :q_start], mismatched[:, :q_start])
    matched_q = matched[:, q_start:]
    mismatched_q = mismatched[:, q_start:]
    assert np.all(np.any(matched_q != mismatched_q, axis=1))
    np.testing.assert_array_equal(
        np.sort(matched_q, axis=0),
        np.sort(mismatched_q, axis=0),
    )
    assert sorted(map(tuple, matched_q.tolist())) == sorted(
        map(tuple, mismatched_q.tolist())
    )


def test_dataset_splits_use_unique_physical_targets() -> None:
    rows = _train_rows()
    entry = _entry()
    curve = Curve(int(entry["field_p"]), 0, 7)
    order = int(entry["group_order"])

    assert len(rows) == min(4096, order - 1)
    all_points = _point_set(rows)
    assert len(all_points) == len(rows)
    assert np.all(rows["scalar"] > 0)
    assert np.all(rows["scalar"] < rows["group_order"])

    expected_generator_roles = {
        "train": {0, 1, 2},
        "seen_curve_seen_generator": {0, 1, 2},
        "seen_curve_new_generator": {3},
    }
    split_point_sets: list[set[tuple[int, int]]] = []
    for name, expected_generators in expected_generator_roles.items():
        subset = rows[rows["split_code"] == SPLITS[name]]
        assert len(subset) > 0
        assert set(int(value) for value in np.unique(subset["generator_index"])) <= (
            expected_generators
        )
        points = _point_set(subset)
        assert len(points) == len(subset)
        split_point_sets.append(points)

    for left_index, left in enumerate(split_point_sets):
        for right in split_point_sets[left_index + 1 :]:
            assert left.isdisjoint(right)

    for row in rows:
        generator = (int(row["gx"]), int(row["gy"]))
        target = (int(row["qx"]), int(row["qy"]))
        assert curve.scalar_mul(int(row["scalar"]), generator) == target


def test_bsgs_and_pollard_rho_recover_known_scalars() -> None:
    entry = _entry()
    curve = Curve(int(entry["field_p"]), 0, 7)
    order = int(entry["group_order"])
    base_raw = entry["base_point"]
    generator = (int(base_raw[0]), int(base_raw[1]))

    for ordinal, scalar in enumerate((1, 2, 17, 1234, order - 1)):
        target = curve.scalar_mul(scalar, generator)
        assert target is not None
        bsgs_candidate, bsgs_operations, memory_bytes = bsgs_solve(
            curve, order, generator, target
        )
        rho_candidate, rho_operations = pollard_rho_solve(
            curve,
            order,
            generator,
            target,
            seed=10_000 + ordinal,
        )
        assert bsgs_candidate == scalar
        assert rho_candidate == scalar
        assert bsgs_operations > 0
        assert rho_operations > 0
        assert memory_bytes > 0


def test_tiny_model_emits_finite_multibit_probabilities() -> None:
    records = _train_rows()
    train = records[:256]
    validation = records[256:288]
    train_features = FeatureStore(train, 13).get("compressed_relation_bits")
    validation_features = FeatureStore(validation, 13).get(
        "compressed_relation_bits"
    )
    labels = scalar_bits(train, 13)
    architecture = {
        "family": "mlp",
        "params": {
            "epochs": 2,
            "hidden_layers": [8],
            "activation": "relu",
            "alpha": 1e-4,
            "batch_size": 32,
            "learning_rate_init": 1e-3,
        },
    }
    model = build_model(architecture, seed=73, jobs=1, output_bits=13)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model.fit(train_features, labels)
    probabilities = predict_probabilities(model, validation_features, bits=13)

    assert probabilities.shape == (len(validation), 13)
    assert probabilities.dtype == np.float64
    assert np.isfinite(probabilities).all()
    assert np.all(probabilities > 0.0)
    assert np.all(probabilities < 1.0)


def test_public_uniform_scalar_prior_is_exact() -> None:
    records = _train_rows()[:3].copy()
    order = int(records[0]["group_order"])
    records["group_order"] = order
    observed = public_uniform_scalar_prior(records, 13)
    labels = np.asarray(
        [
            [(scalar >> bit) & 1 for bit in range(12, -1, -1)]
            for scalar in range(1, order)
        ],
        dtype=np.float64,
    )
    expected = labels.mean(axis=0)
    np.testing.assert_allclose(
        observed,
        np.repeat(expected[None, :], len(records), axis=0),
        atol=0.0,
        rtol=0.0,
    )


def test_ledger_finalization_and_exclusive_output_lock() -> None:
    rows = [
        {
            "stage": "screen",
            "field_bits": 13,
            "architecture_id": "a",
            "seed": seed,
        }
        for seed in (101, 211, 307)
    ]
    with TemporaryDirectory() as temporary_directory:
        base = Path(temporary_directory)
        ledger_path = base / "selection_ledger.jsonl"
        finalize_success_ledger(ledger_path, rows, expected_count=3)
        replayed = [
            json.loads(line)
            for line in ledger_path.read_text(encoding="utf-8").splitlines()
        ]
        assert len(replayed) == 3
        assert {row["seed"] for row in replayed} == {101, 211, 307}
        assert all(row["status"] == "success" for row in replayed)

        duplicate_rows = [rows[0], copy.deepcopy(rows[0])]
        try:
            finalize_success_ledger(
                ledger_path,
                duplicate_rows,
                expected_count=2,
            )
        except RuntimeError as error:
            assert "duplicate run identities" in str(error)
        else:
            raise AssertionError("duplicate ledger identities were accepted")

        output_dir = base / "reports"
        with exclusive_output_lock(output_dir):
            try:
                with exclusive_output_lock(output_dir):
                    raise AssertionError("nested output lock was acquired")
            except RuntimeError as error:
                assert "already in use" in str(error)


def main() -> int:
    test_curve_order_and_hasse_certificate()
    test_glv_and_generator_orbits()
    test_public_features_never_read_scalar()
    test_mismatched_relation_rotates_q_and_preserves_marginals()
    test_dataset_splits_use_unique_physical_targets()
    test_bsgs_and_pollard_rho_recover_known_scalars()
    test_tiny_model_emits_finite_multibit_probabilities()
    test_public_uniform_scalar_prior_is_exact()
    test_ledger_finalization_and_exclusive_output_lock()
    print("P1 TOY-SCALING TESTS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
