#!/usr/bin/env python3
"""Run the preregistered P1E AutoML scaling assay."""
from __future__ import annotations

import argparse
import copy
import fcntl
import hashlib
import heapq
import json
import math
import os
import pickle
import platform
import statistics
import subprocess
import sys
import tempfile
import time
import warnings
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import scipy
import sklearn
from scipy.stats import t as student_t
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.kernel_approximation import RBFSampler
from sklearn.linear_model import Ridge
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline

try:
    from .curve_math import Curve
    from .representations import FeatureStore, scalar_bits
except ImportError:
    from curve_math import Curve
    from representations import FeatureStore, scalar_bits


EPSILON = 1e-12
SPLIT_NAMES = (
    "seen_curve_seen_generator",
    "seen_curve_new_generator",
    "new_curve_seen_generator",
    "new_curve_new_generator",
    "blind_curve_blind_generator",
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


def source_dependency_hashes() -> dict[str, str]:
    package_dir = Path(__file__).resolve().parent
    return {
        name: sha256_file(package_dir / name)
        for name in ("run_assay.py", "representations.py", "curve_math.py")
    }


def git_output(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.strip()


def git_is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    return (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, descendant],
            cwd=root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    )


def clean_source_state(root: Path) -> dict[str, Any]:
    state = {
        "source_commit": git_output(root, "rev-parse", "HEAD"),
        "source_worktree_dirty_before_run": bool(
            git_output(root, "status", "--porcelain")
        ),
    }
    if state["source_worktree_dirty_before_run"]:
        raise RuntimeError("P1E assay requires a clean committed source tree")
    return state


def append_ledger(path: Path, item: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n")


@contextmanager
def exclusive_output_lock(output_dir: Path) -> Any:
    """Prevent two assay processes from mutating the same output directory."""
    output_token = hashlib.sha256(
        str(output_dir.resolve()).encode("utf-8")
    ).hexdigest()
    lock_path = (
        Path(tempfile.gettempdir()) / f"p1e-toy-scaling-{output_token}.lock"
    )
    handle = lock_path.open("a+", encoding="utf-8")
    try:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError(
                f"P1E output directory is already in use: {output_dir}"
            ) from error
        handle.seek(0)
        handle.truncate()
        handle.write(f"pid={os.getpid()}\noutput={output_dir.resolve()}\n")
        handle.flush()
        yield
    finally:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def finalize_success_ledger(
    path: Path,
    rows: list[dict[str, Any]],
    expected_count: int,
) -> None:
    """Atomically rewrite and read back a complete successful-run ledger."""
    if len(rows) != expected_count:
        raise RuntimeError(
            f"P1E ledger row count {len(rows)} != {expected_count}"
        )
    items = []
    identities = []
    for row in rows:
        item = dict(row)
        item["status"] = "success"
        items.append(item)
        identities.append(
            (
                item.get("stage"),
                item.get("field_bits"),
                item.get("architecture_id"),
                item.get("seed"),
                item.get("control_id"),
            )
        )
    if len(set(identities)) != expected_count:
        raise RuntimeError("P1E ledger contains duplicate run identities")
    payload = "".join(
        json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n"
        for item in items
    ).encode("utf-8")
    temporary_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary_path.open("wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)
    if path.read_bytes() != payload:
        raise RuntimeError("P1E ledger read-back differs from canonical rows")
    replayed = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    ]
    if len(replayed) != expected_count or any(
        item.get("status") != "success" for item in replayed
    ):
        raise RuntimeError("P1E ledger read-back matrix is incomplete")


@dataclass
class SizeData:
    bits: int
    records: dict[str, np.ndarray]
    stores: dict[str, FeatureStore]
    source_files: tuple[str, ...]


def load_size_data(
    bits: int,
    manifest: dict[str, Any],
    dataset_dir: Path,
    allowed_splits: list[str],
) -> SizeData:
    codes = {name: int(code) for name, code in manifest["split_codes"].items()}
    allowed = set(allowed_splits)
    if not allowed <= set(codes):
        raise ValueError("unknown split requested from P1E manifest")
    selected_entries = []
    for entry in manifest["files"]:
        if int(entry["field_bits"]) != bits:
            continue
        present = {
            name
            for name, count in entry["split_counts"].items()
            if int(count) > 0
        }
        if present & allowed:
            if not present <= allowed:
                raise ValueError(
                    "dataset shard crosses the requested blind boundary"
                )
            selected_entries.append(entry)
    if not selected_entries:
        raise ValueError(f"no P1E shards available for {bits} bits")
    matrices = []
    source_files = []
    for entry in selected_entries:
        path = dataset_dir / entry["relative_path"]
        if sha256_file(path) != entry["sha256"]:
            raise ValueError(f"dataset shard hash mismatch: {path.name}")
        matrices.append(np.load(path, mmap_mode="r", allow_pickle=False))
        source_files.append(path.name)
    all_records = (
        np.asarray(matrices[0])
        if len(matrices) == 1
        else np.concatenate(matrices)
    )
    records = {
        name: np.asarray(all_records[all_records["split_code"] == code])
        for name, code in codes.items()
        if name in allowed
    }
    if any(not len(records[name]) for name in allowed):
        raise ValueError(f"an allowed P1E split is empty at {bits} bits")
    return SizeData(
        bits=bits,
        records=records,
        stores={name: FeatureStore(value, bits) for name, value in records.items()},
        source_files=tuple(sorted(source_files)),
    )


def architecture_for_stage(
    architecture: dict[str, Any], config: dict[str, Any], stage: str
) -> dict[str, Any]:
    rendered = copy.deepcopy(architecture)
    if rendered["family"] in {"mlp", "rbf_logistic"}:
        rendered["params"]["epochs"] = int(config["stage_epoch_caps"][stage])
    return rendered


def build_model(
    architecture: dict[str, Any], seed: int, jobs: int, output_bits: int
) -> Any:
    family = architecture["family"]
    params = architecture["params"]
    if family == "ridge":
        return Ridge(alpha=float(params["alpha"]), solver="cholesky")
    if family == "mlp":
        epochs = int(params["epochs"])
        return MLPClassifier(
            hidden_layer_sizes=tuple(params["hidden_layers"]),
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
    if family == "extra_trees":
        depth = int(params["max_depth"])
        trees = int(params["n_estimators"])
        maximum_nodes = (1 << (depth + 1)) - 1
        value_bytes = (
            trees * maximum_nodes * output_bits * 2 * np.dtype(np.float64).itemsize
        )
        if value_bytes > 1_000_000_000:
            raise MemoryError("ExtraTrees value arrays exceed the 1 GB guard")
        return ExtraTreesClassifier(
            n_estimators=trees,
            max_depth=depth,
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
    raise ValueError(f"unknown model family: {family}")


def predict_probabilities(model: Any, features: np.ndarray, bits: int) -> np.ndarray:
    if isinstance(model, Ridge):
        raw = np.asarray(model.predict(features), dtype=np.float64)
        return np.clip(raw, EPSILON, 1.0 - EPSILON)
    raw = model.predict_proba(features)
    if isinstance(raw, list):
        output = np.empty((len(features), len(raw)), dtype=np.float64)
        classes = model.classes_
        for bit, values in enumerate(raw):
            bit_classes = np.asarray(classes[bit])
            columns = np.flatnonzero(bit_classes == 1)
            output[:, bit] = values[:, columns[0]] if len(columns) else 0.0
        return np.clip(output, EPSILON, 1.0 - EPSILON)
    values = np.asarray(raw, dtype=np.float64)
    if values.ndim == 2 and values.shape[1] == bits:
        return np.clip(values, EPSILON, 1.0 - EPSILON)
    if values.ndim == 3 and values.shape[0] == bits:
        output = values[:, :, 1].T
        return np.clip(output, EPSILON, 1.0 - EPSILON)
    raise ValueError(f"unexpected probability shape: {values.shape}")


def cluster_se(values: np.ndarray, groups: np.ndarray) -> tuple[float, int]:
    unique = np.unique(groups)
    means = np.asarray([values[groups == group].mean() for group in unique])
    if len(means) <= 1:
        return float("inf"), len(means)
    return float(means.std(ddof=1) / math.sqrt(len(means))), len(means)


def public_uniform_scalar_prior(
    records: np.ndarray, width: int
) -> np.ndarray:
    """Exact public bit prior for a uniform scalar in [1, n-1]."""
    orders = records["group_order"].astype(np.uint64)
    output = np.empty((len(records), width), dtype=np.float64)
    for column, bit_position in enumerate(range(width - 1, -1, -1)):
        half_period = np.uint64(1 << bit_position)
        period = np.uint64(1 << (bit_position + 1))
        complete = orders // period
        remainder = orders % period
        ones = complete * half_period + np.maximum(
            remainder.astype(np.int64) - int(half_period), 0
        ).astype(np.uint64)
        output[:, column] = ones / (orders - np.uint64(1))
    return output


def beam_recovery(
    probabilities: np.ndarray,
    scalars: np.ndarray,
    orders: np.ndarray,
    widths: list[int],
    sample_limit: int = 1024,
) -> dict[str, Any]:
    count = min(len(probabilities), sample_limit)
    if count == 0:
        return {"sample_records": 0, "recovery": {str(k): 0.0 for k in widths}}
    indices = np.linspace(0, len(probabilities) - 1, count, dtype=np.int64)
    maximum = max(widths)
    hits = {width: 0 for width in widths}
    ranks: list[int | None] = []
    for index in indices:
        order = int(orders[index])
        beam: list[tuple[float, int]] = [(0.0, 0)]
        output_width = probabilities.shape[1]
        for bit_index, probability in enumerate(probabilities[index]):
            log_zero = math.log(max(EPSILON, 1.0 - float(probability)))
            log_one = math.log(max(EPSILON, float(probability)))
            remaining_bits = output_width - bit_index - 1
            expanded = []
            for score, value in beam:
                for bit in (0, 1):
                    prefix = (value << 1) | bit
                    minimum = prefix << remaining_bits
                    maximum_possible = ((prefix + 1) << remaining_bits) - 1
                    if minimum >= order or maximum_possible < 1:
                        continue
                    expanded.append(
                        (score + (log_one if bit else log_zero), prefix)
                    )
            beam = heapq.nlargest(maximum, expanded, key=lambda item: item[0])
        valid = [value for _, value in beam if 0 < value < order]
        true_scalar = int(scalars[index])
        rank = valid.index(true_scalar) + 1 if true_scalar in valid else None
        ranks.append(rank)
        for width in widths:
            if rank is not None and rank <= width:
                hits[width] += 1
    return {
        "sample_records": count,
        "recovery": {str(width): hits[width] / count for width in widths},
        "median_true_rank_when_recovered": (
            float(statistics.median(rank for rank in ranks if rank is not None))
            if any(rank is not None for rank in ranks)
            else None
        ),
    }


def metrics(
    true_bits: np.ndarray,
    probabilities: np.ndarray,
    public_prior: np.ndarray,
    records: np.ndarray,
    recovery_widths: list[int] | None = None,
) -> dict[str, Any]:
    true = true_bits.astype(np.float64)
    predicted = np.clip(
        probabilities.astype(np.float64), EPSILON, 1.0 - EPSILON
    )
    prior = np.clip(
        public_prior.astype(np.float64), EPSILON, 1.0 - EPSILON
    )
    model_loss = -(
        true * np.log2(predicted) + (1.0 - true) * np.log2(1.0 - predicted)
    )
    prior_loss = -(
        true * np.log2(prior) + (1.0 - true) * np.log2(1.0 - prior)
    )
    information_by_key = (prior_loss - model_loss).sum(axis=1)
    information_by_bit = (prior_loss - model_loss).mean(axis=0)
    predicted_bits = predicted >= 0.5
    prior_bits = prior >= 0.5
    correct = predicted_bits == true
    prior_correct = prior_bits == true
    accuracy_delta_by_key = correct.mean(axis=1) - prior_correct.mean(axis=1)
    groups = records["curve_index"].astype(np.int64)
    information_se, cluster_count = cluster_se(information_by_key, groups)
    accuracy_se, _ = cluster_se(accuracy_delta_by_key, groups)
    info_mean = float(information_by_key.mean())
    accuracy_lift = float(accuracy_delta_by_key.mean())
    critical99 = (
        float(student_t.ppf(0.995, cluster_count - 1))
        if cluster_count > 1
        else float("inf")
    )
    result: dict[str, Any] = {
        "records": len(records),
        "clusters": cluster_count,
        "cluster_unit": "curve",
        "information_gain_bits_per_key": info_mean,
        "information_gain_bits_per_bit": float(information_by_bit.mean()),
        "information_gain_cluster_se": information_se,
        "information_gain_99ci": [
            info_mean - critical99 * information_se,
            info_mean + critical99 * information_se,
        ],
        "bit_accuracy": float(correct.mean()),
        "prior_bit_accuracy": float(prior_correct.mean()),
        "bit_accuracy_lift": accuracy_lift,
        "bit_accuracy_lift_cluster_se": accuracy_se,
        "bit_accuracy_lift_99ci": [
            accuracy_lift - critical99 * accuracy_se,
            accuracy_lift + critical99 * accuracy_se,
        ],
        "cluster_interval_distribution": "Student-t",
        "cluster_interval_critical_99": critical99,
        "mean_hamming": float((~correct).sum(axis=1).mean()),
        "exact_recovery": float(correct.all(axis=1).mean()),
        "exact_recovery_count": int(correct.all(axis=1).sum()),
        "information_gain_by_bit": [float(value) for value in information_by_bit],
    }
    if recovery_widths:
        result["beam"] = beam_recovery(
            predicted,
            records["scalar"],
            records["group_order"],
            recovery_widths,
        )
    return result


def fit_model(
    data: SizeData,
    architecture: dict[str, Any],
    seed: int,
    jobs: int,
    stage: str,
    eval_splits: list[str],
    labels_override: np.ndarray | None = None,
    leaked_bits: int = 0,
    feature_mode_override: str | None = None,
    recovery_widths: list[int] | None = None,
) -> tuple[Any, dict[str, Any], dict[str, np.ndarray]]:
    mode = feature_mode_override or architecture["feature_mode"]
    train_features = data.stores["train"].get(mode, leaked_bits)
    labels = (
        labels_override
        if labels_override is not None
        else scalar_bits(data.records["train"], data.bits)
    )
    model = build_model(architecture, seed, jobs, data.bits)
    started = time.perf_counter()
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        model.fit(train_features, labels)
    fit_seconds = time.perf_counter() - started
    split_metrics: dict[str, Any] = {}
    predictions: dict[str, np.ndarray] = {}
    inference_seconds: dict[str, float] = {}
    for split in eval_splits:
        features = data.stores[split].get(mode, leaked_bits)
        inference_started = time.perf_counter()
        probabilities = predict_probabilities(model, features, data.bits)
        inference_seconds[split] = time.perf_counter() - inference_started
        predictions[split] = probabilities
        split_metrics[split] = metrics(
            scalar_bits(data.records[split], data.bits),
            probabilities,
            public_uniform_scalar_prior(data.records[split], data.bits),
            data.records[split],
            recovery_widths,
        )
    estimator = model.steps[-1][1] if hasattr(model, "steps") else model
    model_meta = {
        "stage": stage,
        "field_bits": data.bits,
        "architecture_id": architecture["id"],
        "family": architecture["family"],
        "feature_mode": mode,
        "params": architecture["params"],
        "seed": seed,
        "train_records": len(labels),
        "feature_columns": train_features.shape[1],
        "fit_seconds": fit_seconds,
        "inference_seconds": inference_seconds,
        "model_bytes_pickle": len(pickle.dumps(model)),
        "warnings": [str(item.message) for item in captured],
        "n_iter": int(getattr(estimator, "n_iter_", 0) or 0),
        "loss_curve": [
            float(value) for value in getattr(estimator, "loss_curve_", [])
        ],
        "metrics": split_metrics,
    }
    return model, model_meta, predictions


def within_cluster_permutation(
    records: np.ndarray, labels: np.ndarray, seed: int
) -> np.ndarray:
    output = labels.copy()
    groups = (
        records["curve_index"].astype(np.int64) * 16
        + records["generator_index"].astype(np.int64)
    )
    generator = np.random.default_rng(seed)
    for group in np.unique(groups):
        indices = np.flatnonzero(groups == group)
        output[indices] = labels[generator.permutation(indices)]
    return output


def independent_random_labels(labels: np.ndarray, seed: int) -> np.ndarray:
    generator = np.random.default_rng(seed)
    return generator.integers(0, 2, size=labels.shape, dtype=np.uint8)


def architecture_scores(
    rows: list[dict[str, Any]], primary_splits: list[str]
) -> list[dict[str, Any]]:
    grouped: dict[str, list[float]] = {}
    for row in rows:
        conservative = min(
            row["metrics"][split]["information_gain_bits_per_key"]
            for split in primary_splits
        )
        grouped.setdefault(row["architecture_id"], []).append(conservative)
    scores = [
        {
            "architecture_id": architecture_id,
            "median_conservative_information_gain": float(statistics.median(values)),
            "minimum_conservative_information_gain": float(min(values)),
            "fits": len(values),
        }
        for architecture_id, values in grouped.items()
    ]
    return sorted(
        scores,
        key=lambda item: (
            -item["median_conservative_information_gain"],
            -item["minimum_conservative_information_gain"],
            item["architecture_id"],
        ),
    )


def corrected_transfer_gate(
    rows: list[dict[str, Any]],
    winner_id: str,
    primary_splits: list[str],
    alpha: float,
) -> dict[str, Any]:
    selected = [row for row in rows if row["architecture_id"] == winner_id]
    comparisons = len(rows) * len(primary_splits)
    checks = []
    for row in selected:
        for split in primary_splits:
            value = row["metrics"][split]
            clusters = int(value["clusters"])
            critical = (
                float(
                    student_t.ppf(
                        1.0 - alpha / max(1, comparisons),
                        clusters - 1,
                    )
                )
                if clusters > 1
                else float("inf")
            )
            info_lower = (
                value["information_gain_bits_per_key"]
                - critical * value["information_gain_cluster_se"]
            )
            accuracy_lower = (
                value["bit_accuracy_lift"]
                - critical * value["bit_accuracy_lift_cluster_se"]
            )
            checks.append(
                {
                    "field_bits": row["field_bits"],
                    "seed": row["seed"],
                    "split": split,
                    "clusters": clusters,
                    "student_t_critical": critical,
                    "information_lower": info_lower,
                    "accuracy_lift_lower": accuracy_lower,
                    "pass": info_lower > 0.0 and accuracy_lower > 0.0,
                }
            )
    return {
        "familywise_alpha": alpha,
        "comparisons": comparisons,
        "selected_comparisons": len(checks),
        "architecture_selection_in_family": True,
        "bonferroni_one_sided_distribution": "Student-t by cluster df",
        "pass": bool(checks) and all(item["pass"] for item in checks),
        "checks": checks,
    }


def counted_scalar_mul(curve: Curve, scalar: int, point: tuple[int, int]) -> tuple[Any, int]:
    result = None
    addend = point
    operations = 0
    remaining = scalar
    while remaining:
        if remaining & 1:
            result = curve.add(result, addend)
            operations += 1
        addend = curve.add(addend, addend)
        operations += 1
        remaining >>= 1
    return result, operations


def bsgs_solve(
    curve: Curve, order: int, generator: tuple[int, int], target: tuple[int, int]
) -> tuple[int | None, int, int]:
    width = math.isqrt(order)
    if width * width < order:
        width += 1
    table: dict[Any, int] = {}
    current = None
    operations = 0
    for value in range(width):
        table.setdefault(current, value)
        current = curve.add(current, generator)
        operations += 1
    stride, extra = counted_scalar_mul(curve, width, generator)
    operations += extra
    negative_stride = curve.negate(stride)
    current = target
    for giant in range(width + 1):
        if current in table:
            candidate = giant * width + table[current]
            if candidate < order and curve.scalar_mul(candidate, generator) == target:
                return candidate, operations, len(table) * 64
        current = curve.add(current, negative_stride)
        operations += 1
    return None, operations, len(table) * 64


def pollard_rho_solve(
    curve: Curve,
    order: int,
    generator: tuple[int, int],
    target: tuple[int, int],
    seed: int,
) -> tuple[int | None, int]:
    maximum_steps = 8 * math.ceil(math.sqrt(order))
    total_operations = 0

    def step(state: tuple[Any, int, int]) -> tuple[Any, int, int]:
        nonlocal total_operations
        point, left, right = state
        partition = 0 if point is None else point[0] % 3
        if partition == 0:
            point = curve.add(point, generator)
            left = (left + 1) % order
        elif partition == 1:
            point = curve.add(point, point)
            left = 2 * left % order
            right = 2 * right % order
        else:
            point = curve.add(point, target)
            right = (right + 1) % order
        total_operations += 1
        return point, left, right

    for restart in range(4):
        digest = hashlib.sha256(
            f"keyai/p1-rho/{seed}/{restart}".encode("ascii")
        ).digest()
        left = 1 + int.from_bytes(digest[:8], "big") % (order - 1)
        right = 1 + int.from_bytes(digest[8:16], "big") % (order - 1)
        left_point, ops_left = counted_scalar_mul(curve, left, generator)
        right_point, ops_right = counted_scalar_mul(curve, right, target)
        total_operations += ops_left + ops_right + 1
        start = (curve.add(left_point, right_point), left, right)
        tortoise = step(start)
        hare = step(step(start))
        for _ in range(maximum_steps):
            if tortoise[0] == hare[0]:
                numerator = (tortoise[1] - hare[1]) % order
                denominator = (hare[2] - tortoise[2]) % order
                if denominator:
                    candidate = numerator * pow(denominator, -1, order) % order
                    if curve.scalar_mul(candidate, generator) == target:
                        return candidate, total_operations
                break
            tortoise = step(tortoise)
            hare = step(step(hare))
    return None, total_operations


def solver_baselines(
    final_data: dict[int, SizeData], targets_per_size: int
) -> list[dict[str, Any]]:
    rows = []
    for bits, data in sorted(final_data.items()):
        records = data.records["blind_curve_blind_generator"]
        if not len(records):
            continue
        indices = np.linspace(
            0, len(records) - 1, min(targets_per_size, len(records)), dtype=np.int64
        )
        for method in ("bsgs", "pollard_rho"):
            successes = 0
            operation_counts = []
            wall_times = []
            memory_bytes = []
            target_runs = []
            for ordinal, index in enumerate(indices):
                row = records[index]
                curve = Curve(int(row["field_p"]), 0, 7)
                generator = (int(row["gx"]), int(row["gy"]))
                target = (int(row["qx"]), int(row["qy"]))
                started = time.perf_counter()
                if method == "bsgs":
                    candidate, operations, memory = bsgs_solve(
                        curve, int(row["group_order"]), generator, target
                    )
                    memory_bytes.append(memory)
                else:
                    candidate, operations = pollard_rho_solve(
                        curve,
                        int(row["group_order"]),
                        generator,
                        target,
                        seed=bits * 1000 + ordinal,
                    )
                    memory_bytes.append(1024)
                wall_times.append(time.perf_counter() - started)
                operation_counts.append(operations)
                successes += int(candidate == int(row["scalar"]))
                target_runs.append(
                    {
                        "sample_ordinal": ordinal,
                        "record_index": int(index),
                        "curve_index": int(row["curve_index"]),
                        "generator_index": int(row["generator_index"]),
                        "expected_scalar": int(row["scalar"]),
                        "candidate_scalar": (
                            int(candidate) if candidate is not None else None
                        ),
                        "group_operations": int(operations),
                        "wall_time_seconds": wall_times[-1],
                        "memory_bytes": int(memory_bytes[-1]),
                    }
                )
            rows.append(
                {
                    "field_bits": bits,
                    "method": method,
                    "targets": len(indices),
                    "successes": successes,
                    "success_rate": successes / len(indices),
                    "median_group_operations": float(statistics.median(operation_counts)),
                    "median_wall_time_seconds": float(statistics.median(wall_times)),
                    "peak_memory_bytes": int(max(memory_bytes)),
                    "memory_is_estimate": True,
                    "measurement_mode": (
                        "cold start; any table is rebuilt for every target"
                    ),
                    "precomputation_reusable_for_same_curve_generator": (
                        method == "bsgs"
                    ),
                    "runs": target_runs,
                }
            )
    return rows


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# P1E toy-curve ML scaling report",
        "",
        "## Decision boundary",
        "",
        "This is a route-neutral engineering qualification. It is not a native "
        "Research Engine outcome and makes no secp256k1 or asymptotic claim.",
        f"Dataset records: {result['dataset_records']}.",
        (
            "The selected architecture is retrained independently at each "
            "size; this is not cross-size weight extrapolation."
        ),
        "",
        "## Search",
        "",
        f"- Screen fits: {result['selection_run_counts']['screen']}",
        (
            "- Selection fits: "
            f"{result['selection_run_counts']['successful']} successful, "
            f"{result['selection_run_counts']['failed']} failed"
        ),
        (
            "- Frozen evaluation fits: "
            f"{result['run_counts']['successful']} successful, "
            f"{result['run_counts']['failed']} failed"
        ),
        f"- Frozen architecture: `{result['frozen_recipe']['architecture']['id']}`",
        f"- Corrected transfer gate: `{result['screen_gate']['pass']}`",
        (
            "- Independent pre-blind selection validation: `pass` "
            f"(`{result['selection_validation_sha256'][:12]}`)"
        ),
        f"- Metric baseline: {result['metric_baseline']}",
        "",
        "## Frozen ladder",
        "",
        "| bits | split | info bits/key | bit lift | exact | top-256 |",
        "|---:|---|---:|---:|---:|---:|",
    ]
    for row in result["frozen_ladder"]:
        for split, value in row["metrics"].items():
            top = value.get("beam", {}).get("recovery", {}).get("256", 0.0)
            lines.append(
                f"| {row['field_bits']} | {split} | "
                f"{value['information_gain_bits_per_key']:.6g} | "
                f"{value['bit_accuracy_lift']:.6g} | "
                f"{value['exact_recovery']:.6g} | {top:.6g} |"
            )
    lines += [
        "",
        "## Controls",
        "",
        f"- Pipeline valid: `{result['controls']['pipeline_valid']}`",
        f"- Canary pass: `{result['controls']['canary_pass']}`",
        f"- Negative-control pass: `{result['controls']['negative_pass']}`",
        "",
        "## Matched generic baselines",
        "",
        "| bits | method | success | median group ops | median seconds |",
        "|---:|---|---:|---:|---:|",
    ]
    for row in result["solver_baselines"]:
        lines.append(
            f"| {row['field_bits']} | {row['method']} | "
            f"{row['success_rate']:.3f} | {row['median_group_operations']:.1f} | "
            f"{row['median_wall_time_seconds']:.6g} |"
        )
    lines += [
        "",
        "Generic baselines are cold-start measurements. The BSGS table is "
        "rebuilt per target here, although it can be reused for additional "
        "targets sharing the same curve and generator. Memory values are "
        "explicit estimates, not process peak-RSS measurements.",
        "",
        "## Interpretation rule",
        "",
        "A result limited to seen curves and generators is memorization or an "
        "instance-specific representation effect. Sizes 28 and 32 remain closed "
        "unless blind 24-bit curve-and-generator transfer yields an independently "
        "verified explicit mechanism with scaling better than the square-root baseline.",
        "",
    ]
    return "\n".join(lines)


def document_payload_hash(document: dict[str, Any], field: str) -> str:
    payload = dict(document)
    payload.pop(field, None)
    return hashlib.sha256(canonical_json(payload)).hexdigest()


def validate_input_bindings(
    config: dict[str, Any],
    catalog: dict[str, Any],
    manifest: dict[str, Any],
    config_path: Path,
    preregistration_path: Path,
    catalog_path: Path,
    manifest_path: Path,
    curve_validation_path: Path,
    dataset_validation_path: Path,
) -> None:
    config_sha = sha256_file(config_path)
    catalog_sha = sha256_file(catalog_path)
    manifest_sha = sha256_file(manifest_path)
    experiment_id = config["experiment_id"]
    preregistration = json.loads(
        preregistration_path.read_text(encoding="utf-8")
    )
    if (
        preregistration.get("experiment_id") != experiment_id
        or preregistration.get("status")
        != "catalog_and_dataset_validated_selection_authorized"
        or preregistration.get("authorized_field_bits")
        != config["field_bits"]
        or preregistration.get("native_research_engine_run") is not False
    ):
        raise ValueError("preregistration does not authorize P1E selection")
    if catalog.get("experiment_id") != experiment_id:
        raise ValueError("catalog experiment mismatch")
    if catalog.get("source_worktree_dirty") is not False:
        raise ValueError("catalog was not generated from a clean source tree")
    if catalog.get("config_sha256") != config_sha:
        raise ValueError("catalog/config binding mismatch")
    if catalog.get("catalog_sha256") != document_payload_hash(
        catalog, "catalog_sha256"
    ):
        raise ValueError("catalog payload hash mismatch")
    if manifest.get("experiment_id") != experiment_id:
        raise ValueError("manifest experiment mismatch")
    if manifest.get("config_sha256") != config_sha:
        raise ValueError("manifest/config binding mismatch")
    if manifest.get("catalog_sha256") != catalog_sha:
        raise ValueError("manifest/catalog binding mismatch")
    if manifest.get("catalog_payload_sha256") != catalog.get(
        "catalog_sha256"
    ):
        raise ValueError("manifest/catalog payload binding mismatch")
    if manifest.get("manifest_sha256") != document_payload_hash(
        manifest, "manifest_sha256"
    ):
        raise ValueError("manifest payload hash mismatch")
    curve_validation = json.loads(
        curve_validation_path.read_text(encoding="utf-8")
    )
    package_dir = Path(__file__).resolve().parent
    oracle_path = (
        Path(__file__).resolve().parents[3]
        / "experiments"
        / "framework"
        / "ec_oracle.py"
    )
    if (
        curve_validation.get("status") != "pass"
        or curve_validation.get("catalog_sha256") != catalog_sha
        or int(curve_validation.get("curve_count", -1))
        != int(catalog["curve_count"])
        or curve_validation.get("validator_sha256")
        != sha256_file(package_dir / "validate_curves.py")
        or curve_validation.get("oracle_sha256") != sha256_file(oracle_path)
    ):
        raise ValueError("curve validation does not authorize this catalog")
    dataset_validation = json.loads(
        dataset_validation_path.read_text(encoding="utf-8")
    )
    if (
        dataset_validation.get("status") != "pass"
        or dataset_validation.get("manifest_sha256") != manifest_sha
        or dataset_validation.get("full_ec_replay") is not True
        or int(dataset_validation.get("ec_checks", -1))
        != int(manifest["records"])
        or int(dataset_validation.get("records", -1))
        != int(manifest["records"])
        or dataset_validation.get("validator_sha256")
        != sha256_file(package_dir / "validate_dataset.py")
        or dataset_validation.get("oracle_sha256") != sha256_file(oracle_path)
    ):
        raise ValueError(
            "full independent dataset replay does not authorize this manifest"
        )
    expected_bindings = {
        "source_commit": catalog.get("source_commit"),
        "config_sha256": config_sha,
        "catalog_file_sha256": catalog_sha,
        "catalog_payload_sha256": catalog.get("catalog_sha256"),
        "manifest_file_sha256": manifest_sha,
        "manifest_payload_sha256": manifest.get("manifest_sha256"),
        "curve_validation_sha256": sha256_file(curve_validation_path),
        "dataset_validation_sha256": sha256_file(dataset_validation_path),
        "dataset_records": int(manifest["records"]),
        "full_ec_replay": True,
    }
    if preregistration.get("frozen_bindings") != expected_bindings:
        raise ValueError("preregistration frozen bindings mismatch")


def execute_controls(
    config: dict[str, Any],
    architectures: dict[str, dict[str, Any]],
    final_architecture: dict[str, Any],
    get_data: Any,
    ledger_path: Path,
    jobs: int,
    run_counts: dict[str, int],
) -> dict[str, Any]:
    evaluation_splits = [
        "seen_curve_seen_generator",
        "seen_curve_new_generator",
        "new_curve_seen_generator",
        "new_curve_new_generator",
    ]
    primary_splits = list(config["selection"]["primary_splits"])
    controls_rows = []
    canary_id = config["controls"]["canary_architecture_id"]
    canary_base = architectures[canary_id]
    control_field_bits = (
        int(config["selection_field_bits"][0]),
        int(config["confirmation_field_bits"][0]),
    )
    for bits in control_field_bits:
        data = get_data(bits)
        negative_architecture = architecture_for_stage(
            final_architecture, config, "controls"
        )
        canary_architecture = architecture_for_stage(
            canary_base, config, "controls"
        )
        seed = int(config["seeds"][0])
        labels = scalar_bits(data.records["train"], bits)
        controls = [
            (
                "random_labels",
                negative_architecture,
                {
                    "labels_override": independent_random_labels(
                        labels, seed + bits
                    )
                },
            ),
            (
                "permuted_labels",
                negative_architecture,
                {
                    "labels_override": within_cluster_permutation(
                        data.records["train"], labels, seed
                    )
                },
            ),
            (
                "opaque_points",
                negative_architecture,
                {"feature_mode_override": "opaque_relation_bits"},
            ),
            (
                "curve_generator_only",
                negative_architecture,
                {"feature_mode_override": "curve_generator_only_bits"},
            ),
            (
                "mismatched_points",
                negative_architecture,
                {"feature_mode_override": "mismatched_relation_bits"},
            ),
            ("leak_1", canary_architecture, {"leaked_bits": 1}),
            ("leak_4", canary_architecture, {"leaked_bits": 4}),
            ("leak_all", canary_architecture, {"leaked_bits": bits}),
        ]
        for control_id, architecture, kwargs in controls:
            run_counts["controls"] += 1
            try:
                _, row, _ = fit_model(
                    data,
                    architecture,
                    seed,
                    jobs,
                    f"control/{control_id}",
                    evaluation_splits,
                    **kwargs,
                )
                row["control_id"] = control_id
                row["control_spec"] = {
                    "target_transform": (
                        control_id
                        if control_id
                        in {"random_labels", "permuted_labels"}
                        else "unchanged"
                    ),
                    "feature_mode_override": kwargs.get(
                        "feature_mode_override"
                    ),
                    "leaked_bits": int(kwargs.get("leaked_bits", 0)),
                }
                controls_rows.append(row)
                append_ledger(ledger_path, {"status": "success", **row})
                run_counts["successful"] += 1
            except Exception as error:
                append_ledger(
                    ledger_path,
                    {
                        "status": "failed",
                        "stage": f"control/{control_id}",
                        "field_bits": bits,
                        "architecture_id": architecture["id"],
                        "seed": seed,
                        "error_type": type(error).__name__,
                        "error": str(error),
                    },
                )
                run_counts["failed"] += 1
    leak_all = [
        row for row in controls_rows if row["control_id"] == "leak_all"
    ]
    leak_one = [
        row for row in controls_rows if row["control_id"] == "leak_1"
    ]
    canary_pass = bool(leak_all and leak_one) and all(
        row["metrics"]["seen_curve_seen_generator"]["exact_recovery"] >= 0.95
        for row in leak_all
    ) and all(
        row["metrics"]["seen_curve_seen_generator"][
            "information_gain_by_bit"
        ][-1]
        > 0.1
        for row in leak_one
    )
    negative_ids = {
        "random_labels",
        "permuted_labels",
        "opaque_points",
        "curve_generator_only",
        "mismatched_points",
    }
    negatives = [
        row
        for row in controls_rows
        if row["control_id"] in negative_ids
    ]
    control_counts = {
        control_id: sum(
            row["control_id"] == control_id for row in controls_rows
        )
        for control_id in negative_ids | {"leak_1", "leak_4", "leak_all"}
    }
    complete_matrix = len(controls_rows) == 16 and all(
        count == 2 for count in control_counts.values()
    )
    negative_pass = bool(negatives) and all(
        not (
            value["information_gain_99ci"][0] > 0.0
            and value["bit_accuracy_lift_99ci"][0] > 0.0
        )
        for row in negatives
        for split, value in row["metrics"].items()
        if split in primary_splits
    )
    return {
        "pipeline_valid": complete_matrix and canary_pass and negative_pass,
        "complete_matrix": complete_matrix,
        "control_counts": control_counts,
        "canary_pass": canary_pass,
        "negative_pass": negative_pass,
        "negative_control_ids": sorted(negative_ids),
        "canary_architecture_id": canary_id,
        "runs": controls_rows,
    }


def run_selection(
    config: dict[str, Any],
    manifest: dict[str, Any],
    config_path: Path,
    preregistration_path: Path,
    catalog_path: Path,
    manifest_path: Path,
    curve_validation_path: Path,
    dataset_validation_path: Path,
    dataset_dir: Path,
    output_dir: Path,
    jobs: int,
    source_state: dict[str, Any],
) -> dict[str, Any]:
    started = time.perf_counter()
    if (
        int(config["selection"]["top_confirmation_recipes"]) != 1
        or config["selection"]["confirmation_may_reselect_architecture"]
        is not False
        or config["selection"][
            "architecture_identity_frozen_after_selection_sizes"
        ]
        is not True
    ):
        raise ValueError("P1E architecture-freeze policy mismatch")
    output_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = output_dir / "selection_ledger.jsonl"
    ledger_path.write_text("", encoding="utf-8")
    architectures = {item["id"]: item for item in config["architectures"]}
    primary_splits = list(config["selection"]["primary_splits"])
    evaluation_splits = [
        "seen_curve_seen_generator",
        "seen_curve_new_generator",
        "new_curve_seen_generator",
        "new_curve_new_generator",
    ]
    run_counts = {
        "screen": 0,
        "confirmation": 0,
        "controls": 0,
        "successful": 0,
        "failed": 0,
    }
    data_cache: dict[int, SizeData] = {}
    allowed_selection_splits = ["train", *evaluation_splits]

    def get_data(bits: int) -> SizeData:
        if bits not in data_cache:
            data_cache[bits] = load_size_data(
                bits, manifest, dataset_dir, allowed_selection_splits
            )
        return data_cache[bits]

    screen_rows: list[dict[str, Any]] = []
    for bits_raw in config["selection_field_bits"]:
        bits = int(bits_raw)
        data = get_data(bits)
        for architecture_base in config["architectures"]:
            architecture = architecture_for_stage(
                architecture_base, config, "screen"
            )
            for seed_raw in config["seeds"]:
                seed = int(seed_raw)
                run_counts["screen"] += 1
                try:
                    _, row, _ = fit_model(
                        data,
                        architecture,
                        seed,
                        jobs,
                        "screen",
                        evaluation_splits,
                    )
                    append_ledger(ledger_path, {"status": "success", **row})
                    screen_rows.append(row)
                    run_counts["successful"] += 1
                except Exception as error:
                    append_ledger(
                        ledger_path,
                        {
                            "status": "failed",
                            "stage": "screen",
                            "field_bits": bits,
                            "architecture_id": architecture["id"],
                            "seed": seed,
                            "error_type": type(error).__name__,
                            "error": str(error),
                        },
                    )
                    run_counts["failed"] += 1
    expected_screen = (
        len(config["selection_field_bits"])
        * len(config["architectures"])
        * len(config["seeds"])
    )
    if run_counts["failed"] or len(screen_rows) != expected_screen:
        raise RuntimeError("P1E screen attempt matrix is incomplete")
    scores = architecture_scores(screen_rows, primary_splits)
    if not scores:
        raise RuntimeError("all P1E screen fits failed")
    screen_winner_id = scores[0]["architecture_id"]
    screen_gate = corrected_transfer_gate(
        screen_rows,
        screen_winner_id,
        primary_splits,
        float(config["selection"]["positive_familywise_alpha"]),
    )
    confirmation_ids = [screen_winner_id]
    confirmation_rows: list[dict[str, Any]] = []
    for bits_raw in config["confirmation_field_bits"]:
        bits = int(bits_raw)
        data = get_data(bits)
        for architecture_id in confirmation_ids:
            architecture = architecture_for_stage(
                architectures[architecture_id], config, "confirmation"
            )
            for seed_raw in config["seeds"]:
                seed = int(seed_raw)
                run_counts["confirmation"] += 1
                try:
                    _, row, _ = fit_model(
                        data,
                        architecture,
                        seed,
                        jobs,
                        (
                            "confirmation"
                            if screen_gate["pass"]
                            else "frozen_reference_after_null"
                        ),
                        evaluation_splits,
                    )
                    append_ledger(ledger_path, {"status": "success", **row})
                    confirmation_rows.append(row)
                    run_counts["successful"] += 1
                except Exception as error:
                    append_ledger(
                        ledger_path,
                        {
                            "status": "failed",
                            "stage": "confirmation",
                            "field_bits": bits,
                            "architecture_id": architecture_id,
                            "seed": seed,
                            "error_type": type(error).__name__,
                            "error": str(error),
                        },
                    )
                    run_counts["failed"] += 1
    expected_confirmation = (
        len(config["confirmation_field_bits"]) * len(config["seeds"])
    )
    if len(confirmation_rows) != expected_confirmation:
        raise RuntimeError("P1E fixed confirmation matrix is incomplete")
    final_id = screen_winner_id
    controls = execute_controls(
        config,
        architectures,
        architectures[final_id],
        get_data,
        ledger_path,
        jobs,
        run_counts,
    )
    if run_counts["failed"] or len(controls["runs"]) != 16:
        raise RuntimeError("P1E selection/control attempt matrix is incomplete")
    successful_rows = [
        *screen_rows,
        *confirmation_rows,
        *controls["runs"],
    ]
    expected_successful = expected_screen + expected_confirmation + 16
    if run_counts["successful"] != expected_successful:
        raise RuntimeError("P1E successful-run count is incomplete")
    finalize_success_ledger(
        ledger_path,
        successful_rows,
        expected_successful,
    )
    ledger_sha = sha256_file(ledger_path)
    opened_files = sorted(
        {
            path
            for data in data_cache.values()
            for path in data.source_files
        }
    )
    if any("blind" in path for path in opened_files):
        raise RuntimeError("selection opened a blind dataset shard")
    result: dict[str, Any] = {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "stage": "selection_complete_blind_unopened",
        "native_research_engine_outcome": False,
        "metric_baseline": config["selection"]["baseline"],
        "dataset_records": int(manifest["records"]),
        "run_counts": run_counts,
        "architecture_scores": scores,
        "screen_gate": screen_gate,
        "frozen_architecture": architectures[final_id],
        "screen_winner_architecture_id": screen_winner_id,
        "confirmation_architecture_ids": confirmation_ids,
        "adaptive_search_stopped": not screen_gate["pass"],
        "controls": controls,
        "blind_evaluation_authorized": controls["pipeline_valid"],
        "dataset_files_opened": opened_files,
        "blind_dataset_shard_opened": False,
        "selection_ledger_sha256": ledger_sha,
        "config_sha256": sha256_file(config_path),
        "preregistration_sha256": sha256_file(preregistration_path),
        "catalog_sha256": sha256_file(catalog_path),
        "manifest_sha256": sha256_file(manifest_path),
        "curve_validation_sha256": sha256_file(curve_validation_path),
        "dataset_validation_sha256": sha256_file(dataset_validation_path),
        "producer_sha256": sha256_file(Path(__file__)),
        "source_dependency_sha256": source_dependency_hashes(),
        "runtime_versions": {
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "sklearn": sklearn.__version__,
        },
        "wall_time_seconds": time.perf_counter() - started,
        **source_state,
    }
    result["result_payload_sha256"] = document_payload_hash(
        result, "result_payload_sha256"
    )
    result_path = output_dir / "selection_result.json"
    result_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    recipe: dict[str, Any] = {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "freeze_stage": "committed_before_any_blind_curve_evaluation",
        "metric_baseline": config["selection"]["baseline"],
        "dataset_records": int(manifest["records"]),
        "training_protocol": (
            "architecture frozen after "
            + "/".join(
                str(int(bits)) for bits in config["selection_field_bits"]
            )
            + " selection; retrained independently at each size; "
            "no cross-size weight transfer"
        ),
        "architecture": architectures[final_id],
        "screen_winner_architecture_id": screen_winner_id,
        "confirmation_architecture_ids": confirmation_ids,
        "adaptive_search_stopped": not screen_gate["pass"],
        "controls_summary": {
            "pipeline_valid": controls["pipeline_valid"],
            "complete_matrix": controls["complete_matrix"],
            "canary_pass": controls["canary_pass"],
            "negative_pass": controls["negative_pass"],
        },
        "blind_evaluation_authorized": controls["pipeline_valid"],
        "screen_gate": screen_gate,
        "architecture_scores": scores,
        "selection_run_counts": run_counts,
        "dataset_files_opened": opened_files,
        "blind_dataset_shard_opened": False,
        "selection_ledger_sha256": ledger_sha,
        "selection_result_sha256": sha256_file(result_path),
        "selection_result_payload_sha256": result[
            "result_payload_sha256"
        ],
        "config_sha256": sha256_file(config_path),
        "preregistration_sha256": sha256_file(preregistration_path),
        "catalog_sha256": sha256_file(catalog_path),
        "manifest_sha256": sha256_file(manifest_path),
        "curve_validation_sha256": sha256_file(curve_validation_path),
        "dataset_validation_sha256": sha256_file(dataset_validation_path),
        "producer_sha256": sha256_file(Path(__file__)),
        "source_dependency_sha256": source_dependency_hashes(),
        "runtime_versions": {
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "sklearn": sklearn.__version__,
        },
        **source_state,
    }
    recipe["recipe_payload_sha256"] = document_payload_hash(
        recipe, "recipe_payload_sha256"
    )
    recipe_path = output_dir / "frozen_assay_recipe.json"
    recipe_path.write_text(
        json.dumps(recipe, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def validate_frozen_recipe(
    recipe: dict[str, Any],
    config: dict[str, Any],
    config_path: Path,
    preregistration_path: Path,
    catalog_path: Path,
    manifest_path: Path,
    curve_validation_path: Path,
    dataset_validation_path: Path,
    selection_result_path: Path,
    selection_ledger_path: Path,
) -> None:
    if recipe.get("experiment_id") != config["experiment_id"]:
        raise ValueError("frozen recipe experiment mismatch")
    for name, path in (
        ("config_sha256", config_path),
        ("preregistration_sha256", preregistration_path),
        ("catalog_sha256", catalog_path),
        ("manifest_sha256", manifest_path),
        ("curve_validation_sha256", curve_validation_path),
        ("dataset_validation_sha256", dataset_validation_path),
    ):
        if recipe.get(name) != sha256_file(path):
            raise ValueError(f"frozen recipe {name} mismatch")
    expected = document_payload_hash(recipe, "recipe_payload_sha256")
    if recipe.get("recipe_payload_sha256") != expected:
        raise ValueError("frozen recipe payload hash mismatch")
    if recipe.get("producer_sha256") != sha256_file(Path(__file__)):
        raise ValueError("run_assay source changed after recipe freeze")
    if recipe.get("source_dependency_sha256") != source_dependency_hashes():
        raise ValueError("an assay source dependency changed after recipe freeze")
    if recipe.get("runtime_versions") != {
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "sklearn": sklearn.__version__,
    }:
        raise ValueError("ML runtime versions changed after recipe freeze")
    if recipe.get("selection_result_sha256") != sha256_file(
        selection_result_path
    ):
        raise ValueError("frozen recipe selection-result hash mismatch")
    if recipe.get("selection_ledger_sha256") != sha256_file(
        selection_ledger_path
    ):
        raise ValueError("frozen recipe selection-ledger hash mismatch")
    selection_result = json.loads(
        selection_result_path.read_text(encoding="utf-8")
    )
    if selection_result.get("stage") != "selection_complete_blind_unopened":
        raise ValueError("selection result has the wrong stage")
    if selection_result.get(
        "result_payload_sha256"
    ) != document_payload_hash(selection_result, "result_payload_sha256"):
        raise ValueError("selection-result payload hash mismatch")
    if selection_result.get(
        "result_payload_sha256"
    ) != recipe.get("selection_result_payload_sha256"):
        raise ValueError("selection-result payload binding mismatch")
    if selection_result.get("frozen_architecture") != recipe.get(
        "architecture"
    ):
        raise ValueError("selection result and recipe architecture differ")
    if (
        recipe.get("blind_evaluation_authorized") is not True
        or selection_result.get("blind_evaluation_authorized") is not True
        or selection_result.get("controls", {}).get("pipeline_valid")
        is not True
        or selection_result.get("controls", {}).get("complete_matrix")
        is not True
    ):
        raise ValueError("selection controls did not authorize blind evaluation")
    configured = {
        item["id"]: item for item in config["architectures"]
    }
    architecture = recipe.get("architecture")
    if not isinstance(architecture, dict):
        raise ValueError("frozen recipe lacks an architecture")
    architecture_id = architecture.get("id")
    if configured.get(architecture_id) != architecture:
        raise ValueError("frozen architecture differs from the configuration")


def validate_preblind_selection_report(
    report_path: Path,
    recipe: dict[str, Any],
    recipe_path: Path,
    selection_result_path: Path,
    selection_ledger_path: Path,
    config_path: Path,
    preregistration_path: Path,
    catalog_path: Path,
    manifest_path: Path,
    curve_validation_path: Path,
    dataset_validation_path: Path,
) -> tuple[dict[str, Any], str]:
    root = Path(__file__).resolve().parents[3]
    current_commit = git_output(root, "rev-parse", "HEAD")
    report_bytes = report_path.read_bytes()
    try:
        relative_report = report_path.resolve().relative_to(root)
    except ValueError as error:
        raise ValueError(
            "pre-blind validation report is outside the repository"
        ) from error
    committed = subprocess.run(
        [
            "git",
            "show",
            f"{current_commit}:{relative_report.as_posix()}",
        ],
        cwd=root,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if committed.returncode != 0 or committed.stdout != report_bytes:
        raise ValueError(
            "pre-blind validation report differs from committed bytes"
        )
    report = json.loads(report_bytes)
    if report.get("status") != "pass" or report.get("error_count") != 0:
        raise ValueError("independent pre-blind selection validation did not pass")
    if report.get("report_payload_sha256") != document_payload_hash(
        report, "report_payload_sha256"
    ):
        raise ValueError("pre-blind validation payload hash mismatch")
    if (
        report.get("source_worktree_dirty_before_run") is not False
        or report.get("producer_modules_imported") is not False
        or report.get("dataset_files_opened") != []
    ):
        raise ValueError("pre-blind validation independence boundary failed")
    validator_path = Path(__file__).with_name("validate_selection.py")
    result_validator_path = Path(__file__).with_name("validate_results.py")
    if report.get("validator_sha256") != sha256_file(validator_path):
        raise ValueError("pre-blind validator source hash mismatch")
    validator_hashes = report.get("validator_hashes")
    if not isinstance(validator_hashes, dict) or validator_hashes.get(
        "validate_results_sha256"
    ) != sha256_file(result_validator_path):
        raise ValueError("pre-blind helper-validator source hash mismatch")
    expected_bindings = {
        "config_sha256": sha256_file(config_path),
        "preregistration_sha256": sha256_file(preregistration_path),
        "catalog_sha256": sha256_file(catalog_path),
        "manifest_sha256": sha256_file(manifest_path),
        "curve_validation_sha256": sha256_file(curve_validation_path),
        "dataset_validation_sha256": sha256_file(dataset_validation_path),
    }
    if report.get("bindings") != expected_bindings:
        raise ValueError("pre-blind validation input bindings mismatch")
    expected_selection = {
        "selection_result_sha256": sha256_file(selection_result_path),
        "selection_ledger_sha256": sha256_file(selection_ledger_path),
        "recipe_sha256": sha256_file(recipe_path),
        "run_counts": recipe.get("selection_run_counts"),
        "blind_evaluation_authorized": True,
    }
    if report.get("selection") != expected_selection:
        raise ValueError("pre-blind validation selection bindings mismatch")
    provenance = report.get("provenance")
    if (
        not isinstance(provenance, dict)
        or provenance.get("selection_source_commit")
        != recipe.get("source_commit")
        or provenance.get("worktree_clean_before_validation") is not True
    ):
        raise ValueError("pre-blind validation provenance mismatch")
    report_source_commit = str(report.get("source_commit", ""))
    if not report_source_commit or not git_is_ancestor(
        root, report_source_commit, current_commit
    ):
        raise ValueError(
            "pre-blind validation source is not an ancestor of evaluation"
        )
    return report, hashlib.sha256(report_bytes).hexdigest()


def run_evaluation(
    config: dict[str, Any],
    manifest: dict[str, Any],
    recipe: dict[str, Any],
    recipe_path: Path,
    selection_result_path: Path,
    selection_ledger_path: Path,
    selection_validation_path: Path,
    config_path: Path,
    preregistration_path: Path,
    catalog_path: Path,
    manifest_path: Path,
    curve_validation_path: Path,
    dataset_validation_path: Path,
    dataset_dir: Path,
    output_dir: Path,
    raw_dir: Path,
    jobs: int,
    source_state: dict[str, Any],
) -> dict[str, Any]:
    validate_frozen_recipe(
        recipe,
        config,
        config_path,
        preregistration_path,
        catalog_path,
        manifest_path,
        curve_validation_path,
        dataset_validation_path,
        selection_result_path,
        selection_ledger_path,
    )
    (
        selection_validation,
        selection_validation_file_sha256,
    ) = validate_preblind_selection_report(
        selection_validation_path,
        recipe,
        recipe_path,
        selection_result_path,
        selection_ledger_path,
        config_path,
        preregistration_path,
        catalog_path,
        manifest_path,
        curve_validation_path,
        dataset_validation_path,
    )
    started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = output_dir / "evaluation_ledger.jsonl"
    ledger_path.write_text("", encoding="utf-8")
    recovery_widths = [
        int(value) for value in config["recovery"]["beam_widths"]
    ]
    final_architecture = recipe["architecture"]
    final_id = final_architecture["id"]
    run_counts = {
        "frozen": 0,
        "successful": 0,
        "failed": 0,
    }
    data_cache: dict[int, SizeData] = {}
    allowed_evaluation_splits = ["train", *SPLIT_NAMES]
    evaluation_rows: list[dict[str, Any]] = []

    def get_data(bits: int) -> SizeData:
        if bits not in data_cache:
            data_cache[bits] = load_size_data(
                bits, manifest, dataset_dir, allowed_evaluation_splits
            )
        return data_cache[bits]

    frozen_ladder = []
    raw_artifacts = []
    final_data: dict[int, SizeData] = {}
    for bits_raw in config["field_bits"]:
        bits = int(bits_raw)
        data = get_data(bits)
        final_data[bits] = data
        architecture = architecture_for_stage(
            final_architecture,
            config,
            "frozen_blind" if bits in config["blind_field_bits"] else "confirmation",
        )
        split_probability_sums: dict[str, np.ndarray] = {}
        fit_rows = []
        for seed_raw in config["seeds"]:
            seed = int(seed_raw)
            run_counts["frozen"] += 1
            try:
                _, row, predictions = fit_model(
                    data,
                    architecture,
                    seed,
                    jobs,
                    "frozen_ladder",
                    list(SPLIT_NAMES),
                )
                append_ledger(ledger_path, {"status": "success", **row})
                fit_rows.append(row)
                evaluation_rows.append(row)
                run_counts["successful"] += 1
                for split, probabilities in predictions.items():
                    split_probability_sums.setdefault(
                        split, np.zeros_like(probabilities, dtype=np.float64)
                    )
                    split_probability_sums[split] += probabilities
            except Exception as error:
                append_ledger(
                    ledger_path,
                    {
                        "status": "failed",
                        "stage": "frozen_ladder",
                        "field_bits": bits,
                        "architecture_id": final_id,
                        "seed": seed,
                        "error_type": type(error).__name__,
                        "error": str(error),
                    },
                )
                run_counts["failed"] += 1
        if len(fit_rows) != len(config["seeds"]):
            raise RuntimeError(
                f"frozen seed ensemble is incomplete for {bits} bits"
            )
        ensemble_probabilities = {
            split: (values / len(fit_rows)).astype(np.float32)
            for split, values in split_probability_sums.items()
        }
        ensemble_metrics = {
            split: metrics(
                scalar_bits(data.records[split], bits),
                probabilities,
                public_uniform_scalar_prior(data.records[split], bits),
                data.records[split],
                recovery_widths,
            )
            for split, probabilities in ensemble_probabilities.items()
        }
        raw_records = np.concatenate(
            [data.records[split] for split in SPLIT_NAMES]
        )
        raw_probabilities = np.concatenate(
            [ensemble_probabilities[split] for split in SPLIT_NAMES]
        )
        raw_path = raw_dir / f"frozen_predictions_b{bits}.npz"
        np.savez(
            raw_path,
            records=raw_records,
            probabilities=raw_probabilities,
            split_names=np.asarray(SPLIT_NAMES),
        )
        raw_artifacts.append(
            {
                "field_bits": bits,
                "path": raw_path.name,
                "sha256": sha256_file(raw_path),
                "records": len(raw_records),
            }
        )
        frozen_ladder.append(
            {
                "field_bits": bits,
                "successful_seed_fits": len(fit_rows),
                "metrics": ensemble_metrics,
                "fit_seconds_total": sum(
                    row["fit_seconds"] for row in fit_rows
                ),
                "model_bytes_median": float(
                    statistics.median(
                        row["model_bytes_pickle"] for row in fit_rows
                    )
                ),
            }
        )

    expected_frozen = len(config["field_bits"]) * len(config["seeds"])
    if (
        run_counts["failed"]
        or run_counts["successful"] != expected_frozen
        or run_counts["frozen"] != expected_frozen
    ):
        raise RuntimeError("P1E frozen evaluation matrix is incomplete")
    finalize_success_ledger(
        ledger_path,
        evaluation_rows,
        expected_frozen,
    )
    selection_result = json.loads(
        selection_result_path.read_text(encoding="utf-8")
    )
    controls = selection_result["controls"]
    solver_rows = solver_baselines(
        final_data,
        int(config["recovery"]["maximum_bsgs_targets_per_split"]),
    )
    result: dict[str, Any] = {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "classification": config["classification"],
        "native_research_engine_outcome": False,
        "metric_baseline": config["selection"]["baseline"],
        "dataset_records": int(manifest["records"]),
        "training_protocol": recipe["training_protocol"],
        "claim_boundary": (
            "exact toy catalog only; no secp256k1 or asymptotic claim"
        ),
        **source_state,
        "config_sha256": sha256_file(config_path),
        "preregistration_sha256": sha256_file(preregistration_path),
        "catalog_sha256": sha256_file(catalog_path),
        "manifest_sha256": sha256_file(manifest_path),
        "curve_validation_sha256": sha256_file(curve_validation_path),
        "dataset_validation_sha256": sha256_file(dataset_validation_path),
        "frozen_recipe_file_sha256": sha256_file(recipe_path),
        "frozen_recipe_payload_sha256": recipe["recipe_payload_sha256"],
        "selection_result_sha256": sha256_file(selection_result_path),
        "selection_result_payload_sha256": recipe[
            "selection_result_payload_sha256"
        ],
        "selection_ledger_sha256": recipe["selection_ledger_sha256"],
        "selection_validation_sha256": selection_validation_file_sha256,
        "selection_validation_payload_sha256": selection_validation[
            "report_payload_sha256"
        ],
        "selection_validation_source_commit": selection_validation[
            "source_commit"
        ],
        "selection_run_counts": recipe["selection_run_counts"],
        "run_counts": run_counts,
        "architecture_scores": recipe["architecture_scores"],
        "screen_gate": recipe["screen_gate"],
        "frozen_recipe": recipe,
        "frozen_ladder": frozen_ladder,
        "controls": controls,
        "solver_baselines": solver_rows,
        "raw_prediction_artifacts": raw_artifacts,
        "evaluation_ledger_sha256": sha256_file(ledger_path),
        "wall_time_seconds": time.perf_counter() - started,
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "sklearn": sklearn.__version__,
            "platform": platform.platform(),
            "jobs": jobs,
        },
        "deferred_field_bits": config["deferred_field_bits"],
        "deferred_reason": (
            "Requires a positive blind-24 mechanism, immutable candidate, "
            "independent validation, and a new policy decision."
        ),
    }
    result["result_payload_sha256"] = document_payload_hash(
        result, "result_payload_sha256"
    )
    (output_dir / "assay_result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "assay_report.md").write_text(
        render_report(result), encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("select", "evaluate"), required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--curve-validation", type=Path, required=True)
    parser.add_argument("--dataset-validation", type=Path, required=True)
    parser.add_argument("--dataset-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--recipe", type=Path)
    parser.add_argument("--selection-result", type=Path)
    parser.add_argument("--selection-ledger", type=Path)
    parser.add_argument("--selection-validation", type=Path)
    parser.add_argument("--raw-dir", type=Path)
    parser.add_argument("--jobs", type=int, default=8)
    args = parser.parse_args()
    config_path = args.config.resolve()
    preregistration_path = args.preregistration.resolve()
    catalog_path = args.catalog.resolve()
    manifest_path = args.manifest.resolve()
    curve_validation_path = args.curve_validation.resolve()
    dataset_validation_path = args.dataset_validation.resolve()
    dataset_dir = args.dataset_dir.resolve()
    output_dir = args.output_dir.resolve()
    root = Path(__file__).resolve().parents[3]
    if args.stage == "select":
        with exclusive_output_lock(output_dir):
            source_state = clean_source_state(root)
            config = json.loads(config_path.read_text(encoding="utf-8"))
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            validate_input_bindings(
                config,
                catalog,
                manifest,
                config_path,
                preregistration_path,
                catalog_path,
                manifest_path,
                curve_validation_path,
                dataset_validation_path,
            )
            jobs = min(
                max(1, args.jobs),
                int(config["budget"]["max_workers"]),
            )
            result = run_selection(
                config,
                manifest,
                config_path,
                preregistration_path,
                catalog_path,
                manifest_path,
                curve_validation_path,
                dataset_validation_path,
                dataset_dir,
                output_dir,
                jobs,
                source_state,
            )
        print(
            "P1E selection complete with blind unopened: "
            f"{result['run_counts']['successful']} successful fits, "
            f"{result['run_counts']['failed']} failed, "
            f"{result['wall_time_seconds']:.3f}s"
        )
        return 0
    if (
        args.recipe is None
        or args.selection_result is None
        or args.selection_ledger is None
        or args.selection_validation is None
        or args.raw_dir is None
    ):
        parser.error(
            "--stage evaluate requires --recipe, --selection-result, "
            "--selection-ledger, --selection-validation, and --raw-dir"
        )
    with exclusive_output_lock(output_dir):
        source_state = clean_source_state(root)
        config = json.loads(config_path.read_text(encoding="utf-8"))
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        validate_input_bindings(
            config,
            catalog,
            manifest,
            config_path,
            preregistration_path,
            catalog_path,
            manifest_path,
            curve_validation_path,
            dataset_validation_path,
        )
        jobs = min(
            max(1, args.jobs),
            int(config["budget"]["max_workers"]),
        )
        result = run_evaluation(
            config,
            manifest,
            json.loads(args.recipe.resolve().read_text(encoding="utf-8")),
            args.recipe.resolve(),
            args.selection_result.resolve(),
            args.selection_ledger.resolve(),
            args.selection_validation.resolve(),
            config_path,
            preregistration_path,
            catalog_path,
            manifest_path,
            curve_validation_path,
            dataset_validation_path,
            dataset_dir,
            output_dir,
            args.raw_dir.resolve(),
            jobs,
            source_state,
        )
    print(
        f"P1E evaluation complete: {result['run_counts']['successful']} "
        f"successful fits, {result['run_counts']['failed']} failed, "
        f"{result['wall_time_seconds']:.3f}s"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
