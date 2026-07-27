#!/usr/bin/env python3
"""Shared full-key ML utilities for synthetic secp256k1 representation assays.

The scientific target is a 256-column Bernoulli matrix, never a floating-point
encoding of the scalar as one number.  Features are built only from the
compressed public point bytes at offsets 32:65 of each fixed-width record.
"""
from __future__ import annotations

import hashlib
import math
import multiprocessing as mp
import time
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.kernel_approximation import RBFSampler
from sklearn.linear_model import Ridge
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline


P = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16)
N = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16)
RECORD_SIZE = 65
OUTPUT_BITS = 256
EPSILON = 1e-12


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scalar_bits(records: np.ndarray) -> np.ndarray:
    """Return all 256 scalar bits as uint8 without a lossy scalar conversion."""
    return np.unpackbits(records[:, :32], axis=1, bitorder="big")


def compressed_public(records: np.ndarray) -> np.ndarray:
    """Return a copy-free view containing only public bytes."""
    return records[:, 32:]


def _decompress_chunk(payload: bytes) -> bytes:
    public = np.frombuffer(payload, dtype=np.uint8).reshape((-1, 33))
    affine = np.empty((len(public), 64), dtype=np.uint8)
    affine[:, :32] = public[:, 1:]
    for index, row in enumerate(public):
        x_bytes = row[1:].tobytes()
        x = int.from_bytes(x_bytes, "big")
        rhs = (pow(x, 3, P) + 7) % P
        y = pow(rhs, (P + 1) // 4, P)
        expected_parity = int(row[0]) - 2
        if (y & 1) != expected_parity:
            y = P - y
        if pow(y, 2, P) != rhs:
            raise ValueError("compressed point does not decompress on secp256k1")
        affine[index, 32:] = np.frombuffer(y.to_bytes(32, "big"), dtype=np.uint8)
    return affine.tobytes()


def decompress_affine(public: np.ndarray, workers: int) -> np.ndarray:
    """Expand compressed points to x||y bytes using public information only."""
    if public.shape[1] != 33:
        raise ValueError("expected 33-byte compressed public keys")
    chunk_records = 10_000
    payloads = [
        public[start : start + chunk_records].tobytes()
        for start in range(0, len(public), chunk_records)
    ]
    if len(payloads) <= 1 or workers <= 1:
        rendered = [_decompress_chunk(payload) for payload in payloads]
    else:
        context = mp.get_context("spawn")
        with context.Pool(processes=min(workers, len(payloads))) as pool:
            rendered = pool.map(_decompress_chunk, payloads)
    return np.frombuffer(b"".join(rendered), dtype=np.uint8).reshape((-1, 64)).copy()


def informative_compressed_bits(public: np.ndarray) -> np.ndarray:
    parity = (public[:, 0] - 2).astype(np.float32).reshape((-1, 1))
    x_bits = np.unpackbits(public[:, 1:], axis=1, bitorder="big").astype(np.float32)
    bits = np.concatenate((parity, x_bits), axis=1)
    return bits * 2.0 - 1.0


def _limbs16(raw: np.ndarray) -> np.ndarray:
    words = (raw[:, 0::2].astype(np.uint16) << 8) | raw[:, 1::2].astype(np.uint16)
    return words.astype(np.float32) / np.float32(32767.5) - 1.0


@dataclass
class FeatureStore:
    records: np.ndarray
    workers: int

    def __post_init__(self) -> None:
        if (
            self.records.ndim != 2
            or self.records.shape[1] != RECORD_SIZE
            or self.records.dtype != np.uint8
        ):
            raise ValueError("records must be a uint8 matrix with shape (N, 65)")
        prefixes = self.records[:, 32]
        if not np.isin(prefixes, np.array([2, 3], dtype=np.uint8)).all():
            raise ValueError("compressed public-key prefixes must be 02 or 03")
        self._cache: dict[str, np.ndarray] = {}

    def get(self, mode: str) -> np.ndarray:
        if mode in self._cache:
            return self._cache[mode]
        public = compressed_public(self.records)
        if mode == "compressed_bits_264":
            value = (
                np.unpackbits(public, axis=1, bitorder="big").astype(np.float32)
                * 2.0
                - 1.0
            )
        elif mode == "compressed_bits_257":
            value = informative_compressed_bits(public)
        elif mode == "compressed_bytes":
            value = public.astype(np.float32) / np.float32(127.5) - 1.0
        elif mode == "x_limbs16":
            parity = (public[:, 0] - 2).astype(np.float32).reshape((-1, 1))
            value = np.concatenate((parity * 2.0 - 1.0, _limbs16(public[:, 1:])), axis=1)
        elif mode == "byte_popcounts":
            bits = np.unpackbits(public, axis=1, bitorder="big").reshape((-1, 33, 8))
            value = (bits.sum(axis=2).astype(np.float32) - 4.0) / 4.0
        elif mode in ("affine_bytes", "affine_bits_512", "affine_limbs16"):
            affine = self._cache.get("_affine_uint8")
            if affine is None:
                affine = decompress_affine(public, self.workers)
                self._cache["_affine_uint8"] = affine
            if mode == "affine_bytes":
                value = affine.astype(np.float32) / np.float32(127.5) - 1.0
            elif mode == "affine_bits_512":
                value = (
                    np.unpackbits(affine, axis=1, bitorder="big").astype(np.float32)
                    * 2.0
                    - 1.0
                )
            else:
                value = _limbs16(affine)
        elif mode.startswith("bit_interactions_"):
            count = int(mode.rsplit("_", 1)[1])
            base = informative_compressed_bits(public)
            generator = np.random.default_rng(0x4B45594149 + count)
            pairs: set[tuple[int, int]] = set()
            while len(pairs) < count:
                left_index, right_index = sorted(
                    generator.choice(base.shape[1], size=2, replace=False).tolist()
                )
                pairs.add((left_index, right_index))
            ordered_pairs = sorted(pairs)
            left = np.asarray([item[0] for item in ordered_pairs])
            right = np.asarray([item[1] for item in ordered_pairs])
            interactions = base[:, left] * base[:, right]
            value = np.concatenate((base, interactions.astype(np.float32)), axis=1)
        else:
            raise ValueError(f"unknown full-key feature mode: {mode}")
        if not np.isfinite(value).all():
            raise FloatingPointError(f"non-finite feature in mode {mode}")
        self._cache[mode] = np.ascontiguousarray(value, dtype=np.float32)
        return self._cache[mode]


def build_model(architecture: dict[str, Any], seed: int, jobs: int) -> Any:
    family = architecture["family"]
    params = architecture["params"]
    if family == "mlp":
        epochs = int(params["epochs"])
        return MLPClassifier(
            hidden_layer_sizes=tuple(int(value) for value in params["hidden_layers"]),
            activation=params["activation"],
            solver="adam",
            alpha=float(params["alpha"]),
            batch_size=int(params["batch_size"]),
            learning_rate_init=float(params["learning_rate_init"]),
            max_iter=epochs,
            tol=0.0,
            n_iter_no_change=epochs + 1,
            early_stopping=False,
            shuffle=True,
            random_state=seed,
        )
    if family == "ridge":
        return Ridge(
            alpha=float(params["alpha"]),
            solver="cholesky",
            tol=float(params.get("tol", 1e-3)),
        )
    if family == "extra_trees":
        if params["max_depth"] is None:
            raise ValueError("full-key ExtraTrees requires a finite max_depth")
        max_depth = int(params["max_depth"])
        trees = int(params["n_estimators"])
        maximum_nodes = (1 << (max_depth + 1)) - 1
        estimated_value_bytes = (
            trees * maximum_nodes * OUTPUT_BITS * 2 * np.dtype(np.float64).itemsize
        )
        if estimated_value_bytes > 1_000_000_000:
            raise MemoryError(
                "full-key ExtraTrees value arrays exceed the 1 GB safety bound"
            )
        return ExtraTreesClassifier(
            n_estimators=trees,
            max_depth=max_depth,
            min_samples_leaf=int(params["min_samples_leaf"]),
            max_features=params["max_features"],
            criterion="log_loss",
            n_jobs=jobs,
            random_state=seed,
        )
    if family == "rbf_logistic":
        epochs = int(params["epochs"])
        return make_pipeline(
            RBFSampler(
                gamma=float(params["gamma"]),
                n_components=int(params["n_components"]),
                random_state=seed,
            ),
            MLPClassifier(
                hidden_layer_sizes=(),
                activation="identity",
                solver="adam",
                alpha=float(params["alpha"]),
                batch_size=int(params["batch_size"]),
                learning_rate_init=float(params["learning_rate_init"]),
                max_iter=epochs,
                tol=0.0,
                n_iter_no_change=epochs + 1,
                early_stopping=False,
                shuffle=True,
                random_state=seed,
            ),
        )
    raise ValueError(f"unknown full-key model family: {family}")


def _predict_probabilities(model: Any, features: np.ndarray) -> np.ndarray:
    if isinstance(model, Ridge):
        raw = np.asarray(model.predict(features), dtype=np.float64)
        return np.clip(raw, EPSILON, 1.0 - EPSILON)
    raw = model.predict_proba(features)
    if isinstance(raw, list):
        probabilities = np.empty((len(features), len(raw)), dtype=np.float64)
        classes = model.classes_
        for bit, bit_probabilities in enumerate(raw):
            bit_classes = np.asarray(classes[bit])
            one_columns = np.flatnonzero(bit_classes == 1)
            probabilities[:, bit] = (
                bit_probabilities[:, one_columns[0]] if len(one_columns) else 0.0
            )
    else:
        probabilities = np.asarray(raw, dtype=np.float64)
    if probabilities.ndim != 2 or probabilities.shape[1] != OUTPUT_BITS:
        raise ValueError(
            f"expected probability shape (*,{OUTPUT_BITS}), got {probabilities.shape}"
        )
    if not np.isfinite(probabilities).all():
        raise FloatingPointError("model emitted non-finite full-key probabilities")
    return np.clip(probabilities, EPSILON, 1.0 - EPSILON)


class ProbabilityEnsemble:
    """Average Bernoulli probabilities from independently seeded models."""

    def __init__(self, models: list[Any]):
        if not models:
            raise ValueError("an ensemble requires at least one model")
        self.models = models

    def predict_proba(self, features: np.ndarray) -> np.ndarray:
        total: np.ndarray | None = None
        for model in self.models:
            probabilities = _predict_probabilities(model, features)
            if total is None:
                total = probabilities
            else:
                total += probabilities
        assert total is not None
        return total / len(self.models)


def _histogram_quantile(histogram: np.ndarray, quantile: float) -> int:
    target = math.ceil(histogram.sum() * quantile)
    return int(np.searchsorted(np.cumsum(histogram), target, side="left"))


def evaluate_model(
    model: Any,
    features: np.ndarray,
    labels: np.ndarray,
    train_priors: np.ndarray,
    batch_records: int,
    detailed: bool = False,
    exploratory_metrics: bool = True,
) -> dict[str, Any]:
    if labels.shape != (len(features), OUTPUT_BITS):
        raise ValueError("full-key labels must have shape (records, 256)")
    priors = np.clip(np.asarray(train_priors, dtype=np.float64), EPSILON, 1 - EPSILON)
    prior_predictions = priors >= 0.5
    model_bce_by_bit = np.zeros(OUTPUT_BITS, dtype=np.float64)
    null_bce_by_bit = np.zeros(OUTPUT_BITS, dtype=np.float64)
    correct_by_bit = np.zeros(OUTPUT_BITS, dtype=np.int64)
    null_correct_by_bit = np.zeros(OUTPUT_BITS, dtype=np.int64)
    model_only_by_bit = np.zeros(OUTPUT_BITS, dtype=np.int64)
    null_only_by_bit = np.zeros(OUTPUT_BITS, dtype=np.int64)
    hamming_histogram = np.zeros(OUTPUT_BITS + 1, dtype=np.int64)
    top_ks = (1, 4, 8, 16, 32)
    top_correct = {value: 0 for value in top_ks}
    top_null_correct = {value: 0 for value in top_ks}
    key_accuracy_delta_sum = 0.0
    key_accuracy_delta_squared_sum = 0.0
    key_information_sum = 0.0
    key_information_squared_sum = 0.0
    total = 0

    for start in range(0, len(labels), batch_records):
        stop = min(start + batch_records, len(labels))
        y = labels[start:stop].astype(bool, copy=False)
        probabilities = _predict_probabilities(model, features[start:stop])
        predictions = probabilities >= 0.5
        null_predictions = np.broadcast_to(prior_predictions, y.shape)
        correct = predictions == y
        null_correct = null_predictions == y
        model_only = correct & ~null_correct
        null_only = null_correct & ~correct

        model_losses = -(
            y * np.log(probabilities) + (~y) * np.log1p(-probabilities)
        )
        null_losses = -(
            y * np.log(priors) + (~y) * np.log1p(-priors)
        )
        model_bce_by_bit += model_losses.sum(axis=0)
        null_bce_by_bit += null_losses.sum(axis=0)
        correct_by_bit += correct.sum(axis=0, dtype=np.int64)
        null_correct_by_bit += null_correct.sum(axis=0, dtype=np.int64)
        model_only_by_bit += model_only.sum(axis=0, dtype=np.int64)
        null_only_by_bit += null_only.sum(axis=0, dtype=np.int64)
        hamming = (~correct).sum(axis=1, dtype=np.int64)
        hamming_histogram += np.bincount(hamming, minlength=OUTPUT_BITS + 1)
        key_accuracy_delta = (
            correct.astype(np.float64).mean(axis=1)
            - null_correct.astype(np.float64).mean(axis=1)
        )
        key_information = (
            (null_losses - model_losses).sum(axis=1) / math.log(2)
        )
        key_accuracy_delta_sum += float(key_accuracy_delta.sum())
        key_accuracy_delta_squared_sum += float(
            np.dot(key_accuracy_delta, key_accuracy_delta)
        )
        key_information_sum += float(key_information.sum())
        key_information_squared_sum += float(
            np.dot(key_information, key_information)
        )

        if exploratory_metrics:
            confidence = np.abs(probabilities - 0.5)
            selected = np.argpartition(confidence, -max(top_ks), axis=1)[
                :, -max(top_ks) :
            ]
            selected_confidence = np.take_along_axis(confidence, selected, axis=1)
            order = np.argsort(selected_confidence, axis=1)[:, ::-1]
            selected = np.take_along_axis(selected, order, axis=1)
            selected_correct = np.take_along_axis(correct, selected, axis=1)
            selected_null_correct = np.take_along_axis(
                null_correct, selected, axis=1
            )
            for value in top_ks:
                top_correct[value] += int(selected_correct[:, :value].sum())
                top_null_correct[value] += int(
                    selected_null_correct[:, :value].sum()
                )
        total += len(y)

    model_bce_by_bit /= total
    null_bce_by_bit /= total
    information_by_bit = (null_bce_by_bit - model_bce_by_bit) / math.log(2)
    bit_accuracy_by_bit = correct_by_bit / total
    null_accuracy_by_bit = null_correct_by_bit / total
    bit_lift_by_bit = bit_accuracy_by_bit - null_accuracy_by_bit
    discordant_by_bit = model_only_by_bit + null_only_by_bit
    paired_z_by_bit = np.divide(
        model_only_by_bit - null_only_by_bit,
        np.sqrt(discordant_by_bit),
        out=np.zeros(OUTPUT_BITS, dtype=np.float64),
        where=discordant_by_bit > 0,
    )
    key_accuracy_delta_mean = key_accuracy_delta_sum / total
    key_information_mean = key_information_sum / total

    def cluster_standard_error(value_sum: float, squared_sum: float) -> float:
        if total <= 1:
            return 0.0
        centered_sum_squares = max(
            0.0, squared_sum - value_sum * value_sum / total
        )
        sample_variance = centered_sum_squares / (total - 1)
        return math.sqrt(sample_variance / total)

    key_accuracy_delta_se = cluster_standard_error(
        key_accuracy_delta_sum, key_accuracy_delta_squared_sum
    )
    key_information_se = cluster_standard_error(
        key_information_sum, key_information_squared_sum
    )
    global_paired_z = (
        key_accuracy_delta_mean / key_accuracy_delta_se
        if key_accuracy_delta_se > 0
        else 0.0
    )
    information_cluster_z = (
        key_information_mean / key_information_se
        if key_information_se > 0
        else 0.0
    )
    information_per_bit = key_information_mean / OUTPUT_BITS
    bit_accuracy = float(correct_by_bit.sum() / (total * OUTPUT_BITS))
    null_accuracy = float(null_correct_by_bit.sum() / (total * OUTPUT_BITS))
    best_bit = int(np.argmax(information_by_bit))
    worst_bit = int(np.argmin(information_by_bit))
    result: dict[str, Any] = {
        "records": total,
        "output_bits": OUTPUT_BITS,
        "model_bce_nats_per_bit": float(model_bce_by_bit.mean()),
        "null_bce_nats_per_bit": float(null_bce_by_bit.mean()),
        "information_gain_bits_per_bit": information_per_bit,
        "information_gain_bits_per_key": key_information_mean,
        "information_gain_cluster_standard_error": key_information_se,
        "information_gain_cluster_z": information_cluster_z,
        "information_gain_95ci_bits_per_key": [
            key_information_mean - 1.959963984540054 * key_information_se,
            key_information_mean + 1.959963984540054 * key_information_se,
        ],
        "bit_accuracy": bit_accuracy,
        "null_bit_accuracy": null_accuracy,
        "bit_accuracy_lift": bit_accuracy - null_accuracy,
        "paired_accuracy_z": global_paired_z,
        "bit_accuracy_lift_cluster_standard_error": key_accuracy_delta_se,
        "bit_accuracy_lift_95ci": [
            key_accuracy_delta_mean - 1.959963984540054 * key_accuracy_delta_se,
            key_accuracy_delta_mean + 1.959963984540054 * key_accuracy_delta_se,
        ],
        "exact_key_matches": int(hamming_histogram[0]),
        "exact_key_accuracy": float(hamming_histogram[0] / total),
        "mean_hamming_distance": float(
            np.dot(np.arange(OUTPUT_BITS + 1), hamming_histogram) / total
        ),
        "hamming_quantiles": {
            "p01": _histogram_quantile(hamming_histogram, 0.01),
            "p10": _histogram_quantile(hamming_histogram, 0.10),
            "p50": _histogram_quantile(hamming_histogram, 0.50),
            "p90": _histogram_quantile(hamming_histogram, 0.90),
            "p99": _histogram_quantile(hamming_histogram, 0.99),
        },
        "best_information_bit": {
            "bit_big_endian": best_bit,
            "information_gain_bits": float(information_by_bit[best_bit]),
            "accuracy_lift": float(bit_lift_by_bit[best_bit]),
            "paired_z": float(paired_z_by_bit[best_bit]),
        },
        "worst_information_bit": {
            "bit_big_endian": worst_bit,
            "information_gain_bits": float(information_by_bit[worst_bit]),
            "accuracy_lift": float(bit_lift_by_bit[worst_bit]),
            "paired_z": float(paired_z_by_bit[worst_bit]),
        },
        "max_positive_bit_paired_z": float(np.max(paired_z_by_bit)),
        "max_abs_bit_paired_z": float(np.max(np.abs(paired_z_by_bit))),
        "per_bit_significance_is_exploratory": True,
    }
    if exploratory_metrics:
        result["top_confidence"] = {
            str(value): {
                "bits_per_key": value,
                "accuracy": top_correct[value] / (total * value),
                "null_accuracy_same_positions": (
                    top_null_correct[value] / (total * value)
                ),
                "accuracy_lift": (
                    (top_correct[value] - top_null_correct[value]) / (total * value)
                ),
            }
            for value in top_ks
        }
    if detailed:
        result["per_bit"] = {
            "information_gain_bits": [float(value) for value in information_by_bit],
            "accuracy": [float(value) for value in bit_accuracy_by_bit],
            "null_accuracy": [float(value) for value in null_accuracy_by_bit],
            "accuracy_lift": [float(value) for value in bit_lift_by_bit],
            "paired_z": [float(value) for value in paired_z_by_bit],
        }
        result["hamming_histogram"] = [
            int(value) for value in hamming_histogram
        ]
    return result


def fit_and_evaluate(
    architecture: dict[str, Any],
    model_seed: int,
    train_features: np.ndarray,
    train_labels: np.ndarray,
    validation_features: np.ndarray,
    validation_labels: np.ndarray,
    jobs: int,
    prediction_batch_records: int,
    detailed: bool = False,
    exploratory_metrics: bool = True,
) -> tuple[Any, dict[str, Any]]:
    max_train = int(architecture.get("max_train_records", len(train_labels)))
    train_count = min(len(train_labels), max_train)
    x_train = train_features[:train_count]
    y_train = train_labels[:train_count]
    train_priors = (y_train.sum(axis=0, dtype=np.float64) + 1.0) / (
        train_count + 2.0
    )
    model = build_model(architecture, model_seed, jobs)
    started = time.perf_counter()
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        model.fit(x_train, y_train)
    fit_seconds = time.perf_counter() - started
    started = time.perf_counter()
    metrics = evaluate_model(
        model,
        validation_features,
        validation_labels,
        train_priors,
        prediction_batch_records,
        detailed=detailed,
        exploratory_metrics=exploratory_metrics,
    )
    evaluation_seconds = time.perf_counter() - started
    fitted_estimator = model.steps[-1][1] if hasattr(model, "steps") else model
    coefficient_count = sum(
        int(np.asarray(value).size)
        for value in getattr(fitted_estimator, "coefs_", [])
    )
    intercept_count = sum(
        int(np.asarray(value).size)
        for value in getattr(fitted_estimator, "intercepts_", [])
    )
    return model, {
        "train_records": train_count,
        "validation_records": len(validation_labels),
        "fit_seconds": fit_seconds,
        "evaluation_seconds": evaluation_seconds,
        "train_loss_curve": [
            float(value) for value in getattr(fitted_estimator, "loss_curve_", [])
        ],
        "actual_iterations": (
            int(fitted_estimator.n_iter_)
            if getattr(fitted_estimator, "n_iter_", None) is not None
            else None
        ),
        "trainable_parameter_count": coefficient_count + intercept_count,
        "warnings": [
            f"{item.category.__name__}: {str(item.message)[:300]}"
            for item in captured
        ],
        "validation": metrics,
        "train_priors": [float(value) for value in train_priors],
    }


def signal_threshold_crossed(
    metrics: dict[str, Any],
    minimum_information_bits_per_key: float = 0.01,
    minimum_bit_accuracy_lift: float = 0.001,
    minimum_paired_z: float = 5.0,
) -> bool:
    return (
        metrics["information_gain_bits_per_key"]
        >= minimum_information_bits_per_key
        and metrics["bit_accuracy_lift"] >= minimum_bit_accuracy_lift
        and metrics["paired_accuracy_z"] >= minimum_paired_z
        and metrics["information_gain_95ci_bits_per_key"][0] > 0.0
        and metrics["bit_accuracy_lift_95ci"][0] > 0.0
    )
