#!/usr/bin/env python3
"""Independent replay of the P1E selection and evaluation artifacts.

The validator deliberately does not import ``run_assay`` or
``representations``.  It reloads the committed dataset and raw prediction
artifacts, recomputes the reported metrics, decodes scalar candidates, and
checks candidate recovery with the separate framework elliptic-curve oracle.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import heapq
import json
import math
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
from scipy import __version__ as scipy_version
from scipy.stats import t as student_t


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.framework.ec_oracle import Curve, validate_scalar  # noqa: E402


EPSILON = 1e-12
METRIC_ABSOLUTE_TOLERANCE = 1e-9
METRIC_RELATIVE_TOLERANCE = 1e-9
SPLIT_NAMES = (
    "seen_curve_seen_generator",
    "seen_curve_new_generator",
    "new_curve_seen_generator",
    "new_curve_new_generator",
    "blind_curve_blind_generator",
)
SELECTION_EVALUATION_SPLITS = SPLIT_NAMES[:-1]
NEGATIVE_CONTROL_IDS = {
    "random_labels",
    "permuted_labels",
    "opaque_points",
    "curve_generator_only",
    "mismatched_points",
}
CANARY_CONTROL_IDS = {"leak_1", "leak_4", "leak_all"}
CONTROL_IDS = NEGATIVE_CONTROL_IDS | CANARY_CONTROL_IDS
CONTROL_FIELD_BITS = (12, 20)
RUNNER_RELATIVE_PATH = (
    "experiments/ml_structure_probe/p1_toy_scaling/run_assay.py"
)
SOURCE_DEPENDENCY_RELATIVE_PATHS = {
    name: f"experiments/ml_structure_probe/p1_toy_scaling/{name}"
    for name in ("run_assay.py", "representations.py", "curve_math.py")
}
REQUIRED_RECORD_FIELDS = {
    "field_p",
    "group_order",
    "curve_a",
    "curve_b",
    "beta",
    "lambda",
    "gx",
    "gy",
    "qx",
    "qy",
    "scalar",
    "curve_index",
    "generator_index",
    "split_code",
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


def payload_hash(document: dict[str, Any], field: str) -> str:
    value = dict(document)
    value.pop(field, None)
    return hashlib.sha256(canonical_json(value)).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


class Findings:
    """Bounded user-facing findings while retaining the exact error count."""

    def __init__(self, maximum_messages: int = 200) -> None:
        self.maximum_messages = maximum_messages
        self.error_count = 0
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.error_count += 1
        if len(self.errors) < self.maximum_messages:
            self.errors.append(message)

    def warning(self, message: str) -> None:
        if len(self.warnings) < self.maximum_messages:
            self.warnings.append(message)


def compare_values(
    findings: Findings,
    context: str,
    recomputed: object,
    reported: object,
    *,
    absolute_tolerance: float = METRIC_ABSOLUTE_TOLERANCE,
    relative_tolerance: float = METRIC_RELATIVE_TOLERANCE,
) -> None:
    """Recursively compare a recomputed value with a reported value."""
    if isinstance(recomputed, dict):
        if not isinstance(reported, dict):
            findings.error(f"{context}: reported value is not an object")
            return
        missing = set(recomputed) - set(reported)
        extra = set(reported) - set(recomputed)
        if missing:
            findings.error(f"{context}: missing reported keys {sorted(missing)}")
        if extra:
            findings.error(f"{context}: unexpected reported keys {sorted(extra)}")
        for key in sorted(set(recomputed) & set(reported)):
            compare_values(
                findings,
                f"{context}.{key}",
                recomputed[key],
                reported[key],
                absolute_tolerance=absolute_tolerance,
                relative_tolerance=relative_tolerance,
            )
        return
    if isinstance(recomputed, (list, tuple)):
        if not isinstance(reported, (list, tuple)):
            findings.error(f"{context}: reported value is not an array")
            return
        if len(recomputed) != len(reported):
            findings.error(
                f"{context}: array length {len(reported)} != {len(recomputed)}"
            )
            return
        for index, (left, right) in enumerate(zip(recomputed, reported)):
            compare_values(
                findings,
                f"{context}[{index}]",
                left,
                right,
                absolute_tolerance=absolute_tolerance,
                relative_tolerance=relative_tolerance,
            )
        return
    if isinstance(recomputed, (int, np.integer)) and not isinstance(
        recomputed, bool
    ):
        if (
            not isinstance(reported, (int, np.integer))
            or isinstance(reported, bool)
            or int(recomputed) != int(reported)
        ):
            findings.error(
                f"{context}: reported {reported!r}, recomputed {recomputed!r}"
            )
        return
    if (
        isinstance(recomputed, (int, float, np.integer, np.floating))
        and not isinstance(recomputed, bool)
        and isinstance(reported, (int, float, np.integer, np.floating))
        and not isinstance(reported, bool)
    ):
        left = float(recomputed)
        right = float(reported)
        if math.isnan(left) or math.isnan(right):
            if not (math.isnan(left) and math.isnan(right)):
                findings.error(f"{context}: numeric NaN mismatch")
            return
        if math.isinf(left) or math.isinf(right):
            if left != right:
                findings.error(f"{context}: infinite numeric mismatch")
            return
        if not math.isclose(
            left,
            right,
            rel_tol=relative_tolerance,
            abs_tol=absolute_tolerance,
        ):
            findings.error(
                f"{context}: reported {right!r}, recomputed {left!r}"
            )
        return
    if recomputed != reported:
        findings.error(
            f"{context}: reported {reported!r}, recomputed {recomputed!r}"
        )


def safe_child(directory: Path, relative: object, findings: Findings) -> Path | None:
    if not isinstance(relative, str) or not relative:
        findings.error("artifact path must be a nonempty relative string")
        return None
    candidate = (directory / relative).resolve()
    try:
        candidate.relative_to(directory.resolve())
    except ValueError:
        findings.error(f"artifact path escapes its directory: {relative!r}")
        return None
    return candidate


def git_commit_exists(commit: object) -> bool:
    if (
        not isinstance(commit, str)
        or len(commit) != 40
        or any(character not in "0123456789abcdef" for character in commit)
    ):
        return False
    completed = subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return completed.returncode == 0


def git_blob(commit: str, path: Path) -> bytes | None:
    try:
        relative = path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return None
    completed = subprocess.run(
        ["git", "show", f"{commit}:{relative}"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return completed.stdout if completed.returncode == 0 else None


def require_committed_file(
    findings: Findings, commit: object, path: Path, label: str
) -> None:
    if not git_commit_exists(commit):
        findings.error(f"{label}: source commit is missing or invalid")
        return
    committed = git_blob(str(commit), path)
    if committed is None:
        findings.error(f"{label}: file is absent at recorded source commit")
    elif committed != path.read_bytes():
        findings.error(f"{label}: local bytes differ from recorded source commit")


def is_ancestor(ancestor: object, descendant: object) -> bool:
    if not git_commit_exists(ancestor) or not git_commit_exists(descendant):
        return False
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", str(ancestor), str(descendant)],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return completed.returncode == 0


def load_ledger(
    path: Path, findings: Findings, label: str
) -> tuple[list[dict[str, Any]], list[bytes]]:
    entries: list[dict[str, Any]] = []
    raw_lines = path.read_bytes().splitlines(keepends=True)
    if not raw_lines:
        findings.error(f"{label}: ledger is empty")
        return entries, raw_lines
    for line_number, raw in enumerate(raw_lines, start=1):
        try:
            value = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            findings.error(f"{label}:{line_number}: invalid JSON: {error}")
            continue
        if not isinstance(value, dict):
            findings.error(f"{label}:{line_number}: row is not an object")
            continue
        if raw.rstrip(b"\r\n") != canonical_json(value):
            findings.error(
                f"{label}:{line_number}: row is not canonical compact JSON"
            )
        entries.append(value)
    return entries, raw_lines


def ledger_counts(entries: list[dict[str, Any]], kind: str) -> dict[str, int]:
    successful = sum(item.get("status") == "success" for item in entries)
    failed = sum(item.get("status") == "failed" for item in entries)
    if kind == "selection":
        screen = sum(item.get("stage") == "screen" for item in entries)
        confirmation = sum(
            item.get("stage")
            in {"confirmation", "frozen_reference_after_null"}
            for item in entries
        )
        controls = sum(
            str(item.get("stage", "")).startswith("control/")
            for item in entries
        )
        return {
            "screen": screen,
            "confirmation": confirmation,
            "controls": controls,
            "successful": successful,
            "failed": failed,
        }
    frozen = sum(item.get("stage") == "frozen_ladder" for item in entries)
    return {
        "frozen": frozen,
        "successful": successful,
        "failed": failed,
    }


def architecture_scores(
    rows: list[dict[str, Any]], primary_splits: list[str]
) -> list[dict[str, Any]]:
    grouped: dict[str, list[float]] = {}
    for row in rows:
        try:
            conservative = min(
                float(row["metrics"][split]["information_gain_bits_per_key"])
                for split in primary_splits
            )
            grouped.setdefault(str(row["architecture_id"]), []).append(
                conservative
            )
        except (KeyError, TypeError, ValueError):
            continue
    scores = [
        {
            "architecture_id": architecture_id,
            "median_conservative_information_gain": float(
                statistics.median(values)
            ),
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


def architecture_for_stage(
    architecture: dict[str, Any],
    config: dict[str, Any],
    stage: str,
) -> dict[str, Any]:
    rendered = copy.deepcopy(architecture)
    if rendered["family"] in {"mlp", "rbf_logistic"}:
        rendered["params"]["epochs"] = int(
            config["stage_epoch_caps"][stage]
        )
    return rendered


def feature_columns_for_mode(
    mode: str, field_bits: int, leaked_bits: int = 0
) -> int:
    base = {
        "compressed_relation_bits": 4 * field_bits + 2,
        "affine_relation_bits": 6 * field_bits,
        "compressed_relation_glv_bits": 6 * field_bits + 2,
        "mismatched_relation_bits": 4 * field_bits + 2,
        "opaque_relation_bits": 2 * field_bits + 128,
        "curve_generator_only_bits": 3 * field_bits + 1,
    }
    if mode not in base:
        raise ValueError(f"unknown P1E feature mode: {mode}")
    return base[mode] + min(max(0, leaked_bits), field_bits)


def validate_successful_fit_metadata(
    row: dict[str, Any],
    expected_architecture: dict[str, Any],
    expected_feature_mode: str,
    findings: Findings,
    context: str,
    *,
    expected_leaked_bits: int = 0,
) -> None:
    expected = {
        "architecture_id": expected_architecture["id"],
        "family": expected_architecture["family"],
        "feature_mode": expected_feature_mode,
        "params": expected_architecture["params"],
    }
    for field, value in expected.items():
        if row.get(field) != value:
            findings.error(
                f"{context}: {field} differs from the staged frozen recipe"
            )
    try:
        expected_columns = feature_columns_for_mode(
            expected_feature_mode,
            int(row["field_bits"]),
            expected_leaked_bits,
        )
    except (KeyError, TypeError, ValueError) as error:
        findings.error(f"{context}: cannot derive feature width: {error}")
    else:
        if row.get("feature_columns") != expected_columns:
            findings.error(
                f"{context}: feature_columns differs from the independent "
                "representation width"
            )


def corrected_transfer_gate(
    rows: list[dict[str, Any]],
    winner_id: str,
    primary_splits: list[str],
    alpha: float,
) -> dict[str, Any]:
    selected = [row for row in rows if row.get("architecture_id") == winner_id]
    comparisons = len(rows) * len(primary_splits)
    checks: list[dict[str, Any]] = []
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
            information_lower = float(
                value["information_gain_bits_per_key"]
            ) - critical * float(value["information_gain_cluster_se"])
            accuracy_lower = float(
                value["bit_accuracy_lift"]
            ) - critical * float(value["bit_accuracy_lift_cluster_se"])
            checks.append(
                {
                    "field_bits": int(row["field_bits"]),
                    "seed": int(row["seed"]),
                    "split": split,
                    "clusters": clusters,
                    "student_t_critical": critical,
                    "information_lower": information_lower,
                    "accuracy_lift_lower": accuracy_lower,
                    "pass": information_lower > 0.0 and accuracy_lower > 0.0,
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


def scalar_bits(records: np.ndarray, width: int) -> np.ndarray:
    shifts = np.arange(width - 1, -1, -1, dtype=np.uint64)
    values = records["scalar"].astype(np.uint64)
    return ((values[:, None] >> shifts) & np.uint64(1)).astype(np.uint8)


def public_uniform_scalar_prior(
    records: np.ndarray, width: int
) -> np.ndarray:
    """Bit priors for an exactly uniform scalar drawn from [1, n - 1]."""
    orders = records["group_order"].astype(np.uint64)
    output = np.empty((len(records), width), dtype=np.float64)
    for column, bit_position in enumerate(range(width - 1, -1, -1)):
        half_period = np.uint64(1 << bit_position)
        period = np.uint64(1 << (bit_position + 1))
        complete_periods = orders // period
        remainder = orders % period
        tail_ones = np.maximum(
            remainder.astype(np.int64) - int(half_period), 0
        ).astype(np.uint64)
        one_count = complete_periods * half_period + tail_ones
        output[:, column] = one_count / (orders - np.uint64(1))
    return output


def cluster_se(values: np.ndarray, records: np.ndarray) -> tuple[float, int]:
    groups = records["curve_index"].astype(np.int64)
    unique = np.unique(groups)
    means = np.asarray([values[groups == group].mean() for group in unique])
    if len(means) <= 1:
        return float("inf"), len(means)
    return float(means.std(ddof=1) / math.sqrt(len(means))), len(means)


class OracleAudit:
    """Cache curves while validating submitted scalar candidates."""

    def __init__(self, findings: Findings) -> None:
        self.findings = findings
        self.curves: dict[tuple[int, int, int], Curve] = {}
        self.results: dict[tuple[int, ...], bool] = {}
        self.submissions = 0
        self.checks = 0
        self.cache_hits = 0
        self.valid_recoveries = 0
        self.rejected_candidates = 0
        self.out_of_range = 0

    def check(self, row: np.void, candidate: int) -> bool:
        self.submissions += 1
        order = int(row["group_order"])
        if not 0 < candidate < order:
            self.out_of_range += 1
            self.rejected_candidates += 1
            return False
        key = (
            int(row["field_p"]),
            int(row["curve_a"]),
            int(row["curve_b"]),
            int(row["gx"]),
            int(row["gy"]),
            int(row["qx"]),
            int(row["qy"]),
            int(candidate),
        )
        if key in self.results:
            self.cache_hits += 1
            recovered = self.results[key]
            self.valid_recoveries += int(recovered)
            self.rejected_candidates += int(not recovered)
            return recovered
        curve_key = key[:3]
        try:
            curve = self.curves.get(curve_key)
            if curve is None:
                curve = Curve(*curve_key)
                self.curves[curve_key] = curve
            recovered = validate_scalar(
                curve,
                (key[3], key[4]),
                (key[5], key[6]),
                int(candidate),
            )
        except (AssertionError, TypeError, ValueError) as error:
            self.findings.error(f"EC oracle rejected candidate input: {error}")
            recovered = False
        self.checks += 1
        self.valid_recoveries += int(recovered)
        self.rejected_candidates += int(not recovered)
        self.results[key] = recovered
        return recovered


def decode_hard_candidates(probabilities: np.ndarray) -> np.ndarray:
    width = probabilities.shape[1]
    weights = np.left_shift(
        np.uint64(1), np.arange(width - 1, -1, -1, dtype=np.uint64)
    )
    return (probabilities >= 0.5).astype(np.uint64) @ weights


def beam_recovery(
    probabilities: np.ndarray,
    records: np.ndarray,
    widths: list[int],
    oracle: OracleAudit,
    findings: Findings,
    context: str,
    sample_limit: int = 1024,
) -> tuple[dict[str, Any], dict[str, int]]:
    count = min(len(probabilities), sample_limit)
    if count == 0:
        return (
            {
                "sample_records": 0,
                "recovery": {str(width): 0.0 for width in widths},
            },
            {"claimed_hits": 0, "oracle_valid_hits": 0},
        )
    indices = np.linspace(0, len(probabilities) - 1, count, dtype=np.int64)
    maximum = max(widths)
    hits = {width: 0 for width in widths}
    ranks: list[int | None] = []
    oracle_valid_hits = 0
    for index_raw in indices:
        index = int(index_raw)
        beam: list[tuple[float, int]] = [(0.0, 0)]
        order = int(records[index]["group_order"])
        output_width = probabilities.shape[1]
        for bit_index, probability in enumerate(probabilities[index]):
            probability_value = float(probability)
            log_zero = math.log(max(EPSILON, 1.0 - probability_value))
            log_one = math.log(max(EPSILON, probability_value))
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
        true_scalar = int(records[index]["scalar"])
        rank = valid.index(true_scalar) + 1 if true_scalar in valid else None
        ranks.append(rank)
        if rank is not None:
            if oracle.check(records[index], true_scalar):
                oracle_valid_hits += 1
            else:
                findings.error(
                    f"{context}: beam-recovered scalar failed EC replay at row {index}"
                )
        for width in widths:
            if rank is not None and rank <= width:
                hits[width] += 1
    recovered_ranks = [rank for rank in ranks if rank is not None]
    result = {
        "sample_records": count,
        "recovery": {
            str(width): hits[width] / count for width in widths
        },
        "median_true_rank_when_recovered": (
            float(statistics.median(recovered_ranks))
            if recovered_ranks
            else None
        ),
    }
    return result, {
        "claimed_hits": len(recovered_ranks),
        "oracle_valid_hits": oracle_valid_hits,
    }


def recompute_metrics(
    records: np.ndarray,
    probabilities: np.ndarray,
    public_prior: np.ndarray,
    recovery_widths: list[int],
    oracle: OracleAudit,
    findings: Findings,
    context: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    true = scalar_bits(records, probabilities.shape[1]).astype(np.float64)
    predicted = np.clip(
        probabilities.astype(np.float64), EPSILON, 1.0 - EPSILON
    )
    prior = np.clip(
        public_prior.astype(np.float64), EPSILON, 1.0 - EPSILON
    )
    model_loss = -(
        true * np.log2(predicted)
        + (1.0 - true) * np.log2(1.0 - predicted)
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
    accuracy_delta_by_key = (
        correct.mean(axis=1) - prior_correct.mean(axis=1)
    )
    information_se, cluster_count = cluster_se(information_by_key, records)
    accuracy_se, _ = cluster_se(accuracy_delta_by_key, records)
    information_mean = float(information_by_key.mean())
    accuracy_lift = float(accuracy_delta_by_key.mean())
    critical99 = (
        float(student_t.ppf(0.995, cluster_count - 1))
        if cluster_count > 1
        else float("inf")
    )
    hard_candidates = decode_hard_candidates(predicted)
    hard_oracle_recoveries = 0
    hard_label_matches = 0
    hard_in_range = 0
    for index, candidate_raw in enumerate(hard_candidates):
        candidate = int(candidate_raw)
        order = int(records[index]["group_order"])
        recovered = oracle.check(records[index], candidate)
        if 0 < candidate < order:
            hard_in_range += 1
            hard_oracle_recoveries += int(recovered)
            label_match = candidate == int(records[index]["scalar"])
            hard_label_matches += int(label_match)
            if recovered != label_match:
                findings.error(
                    f"{context}: hard candidate/label/EC disagreement at row {index}"
                )
        elif recovered:
            findings.error(
                f"{context}: out-of-range candidate passed EC replay at row {index}"
            )
    beam, beam_audit = beam_recovery(
        predicted,
        records,
        recovery_widths,
        oracle,
        findings,
        context,
    )
    exact_count = int(correct.all(axis=1).sum())
    if exact_count != hard_label_matches:
        findings.error(
            f"{context}: bitwise exact count differs from decoded scalar matches"
        )
    if exact_count != hard_oracle_recoveries:
        findings.error(
            f"{context}: exact-recovery count differs from EC-validated recovery"
        )
    metrics: dict[str, Any] = {
        "records": len(records),
        "clusters": cluster_count,
        "cluster_unit": "curve",
        "information_gain_bits_per_key": information_mean,
        "information_gain_bits_per_bit": float(information_by_bit.mean()),
        "information_gain_cluster_se": information_se,
        "information_gain_99ci": [
            information_mean - critical99 * information_se,
            information_mean + critical99 * information_se,
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
        "exact_recovery": float(exact_count / len(records)),
        "exact_recovery_count": exact_count,
        "information_gain_by_bit": [
            float(value) for value in information_by_bit
        ],
        "beam": beam,
    }
    recovery_audit = {
        "records": len(records),
        "hard_candidates_in_range": hard_in_range,
        "hard_label_matches": hard_label_matches,
        "hard_oracle_valid_recoveries": hard_oracle_recoveries,
        "beam": beam_audit,
    }
    return metrics, recovery_audit


def recompute_control_decision(
    rows: list[dict[str, Any]],
    primary_splits: list[str],
    canary_architecture_id: str,
    findings: Findings,
    context: str,
) -> dict[str, Any]:
    leak_all = [row for row in rows if row.get("control_id") == "leak_all"]
    leak_one = [row for row in rows if row.get("control_id") == "leak_1"]
    try:
        canary_pass = bool(leak_all and leak_one) and all(
            row["metrics"]["seen_curve_seen_generator"]["exact_recovery"]
            >= 0.95
            for row in leak_all
        ) and all(
            row["metrics"]["seen_curve_seen_generator"][
                "information_gain_by_bit"
            ][-1]
            > 0.1
            for row in leak_one
        )
    except (IndexError, KeyError, TypeError):
        findings.error(f"{context}: control canary metrics are incomplete")
        canary_pass = False
    negatives = [
        row for row in rows if row.get("control_id") in NEGATIVE_CONTROL_IDS
    ]
    try:
        negative_pass = bool(negatives) and all(
            not (
                value["information_gain_99ci"][0] > 0.0
                and value["bit_accuracy_lift_99ci"][0] > 0.0
            )
            for row in negatives
            for split, value in row["metrics"].items()
            if split in primary_splits
        )
    except (IndexError, KeyError, TypeError):
        findings.error(f"{context}: negative-control metrics are incomplete")
        negative_pass = False
    control_counts = {
        control_id: sum(row.get("control_id") == control_id for row in rows)
        for control_id in CONTROL_IDS
    }
    complete_matrix = len(rows) == (
        len(CONTROL_FIELD_BITS) * len(CONTROL_IDS)
    ) and all(
        count == len(CONTROL_FIELD_BITS)
        for count in control_counts.values()
    )
    return {
        "pipeline_valid": complete_matrix and canary_pass and negative_pass,
        "complete_matrix": complete_matrix,
        "control_counts": control_counts,
        "canary_pass": canary_pass,
        "negative_pass": negative_pass,
        "negative_control_ids": sorted(NEGATIVE_CONTROL_IDS),
        "canary_architecture_id": canary_architecture_id,
    }


def validate_control_attempt_matrix(
    config: dict[str, Any],
    final_architecture: dict[str, Any],
    entries: list[dict[str, Any]],
    findings: Findings,
    context: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    control_entries = [
        row
        for row in entries
        if str(row.get("stage", "")).startswith("control/")
    ]
    successful_rows = [
        {key: value for key, value in row.items() if key != "status"}
        for row in control_entries
        if row.get("status") == "success"
    ]
    seed = int(config["seeds"][0])
    expected_attempts = {
        (bits, control_id, seed)
        for bits in CONTROL_FIELD_BITS
        for control_id in CONTROL_IDS
    }
    observed_attempts: list[tuple[int, str, int]] = []
    canary_id = str(config["controls"]["canary_architecture_id"])
    configured = {
        str(item["id"]): item for item in config["architectures"]
    }
    for row in control_entries:
        stage = str(row.get("stage", ""))
        control_id = stage.split("/", 1)[1]
        attempt = (
            int(row.get("field_bits", -1)),
            control_id,
            int(row.get("seed", -1)),
        )
        observed_attempts.append(attempt)
        expected_base = (
            configured[canary_id]
            if control_id in CANARY_CONTROL_IDS
            else final_architecture
        )
        if row.get("architecture_id") != expected_base["id"]:
            findings.error(
                f"{context}: control {attempt[:2]} used unexpected "
                f"architecture {row.get('architecture_id')!r}"
            )
        if row.get("status") == "success":
            if row.get("control_id") != control_id:
                findings.error(
                    f"{context}: control {attempt[:2]} has inconsistent "
                    "control_id"
                )
            staged = architecture_for_stage(
                expected_base, config, "controls"
            )
            override_modes = {
                "opaque_points": "opaque_relation_bits",
                "curve_generator_only": "curve_generator_only_bits",
                "mismatched_points": "mismatched_relation_bits",
            }
            leaked_bits = {
                "leak_1": 1,
                "leak_4": 4,
                "leak_all": int(row.get("field_bits", 0)),
            }.get(control_id, 0)
            expected_control_spec = {
                "target_transform": (
                    control_id
                    if control_id in {"random_labels", "permuted_labels"}
                    else "unchanged"
                ),
                "feature_mode_override": override_modes.get(control_id),
                "leaked_bits": leaked_bits,
            }
            if row.get("control_spec") != expected_control_spec:
                findings.error(
                    f"{context}: control {attempt[:2]} has an unexpected "
                    "control_spec"
                )
            validate_successful_fit_metadata(
                row,
                staged,
                override_modes.get(control_id, staged["feature_mode"]),
                findings,
                f"{context} control {attempt[:2]}",
                expected_leaked_bits=leaked_bits,
            )
    if set(observed_attempts) != expected_attempts:
        findings.error(f"{context}: control attempt matrix is incomplete")
    if len(observed_attempts) != len(expected_attempts):
        findings.error(f"{context}: control ledger has duplicate attempts")
    successful_attempts = [
        (
            int(row.get("field_bits", -1)),
            str(row.get("stage", "")).split("/", 1)[1],
            int(row.get("seed", -1)),
        )
        for row in control_entries
        if row.get("status") == "success"
    ]
    if (
        set(successful_attempts) != expected_attempts
        or len(successful_attempts) != len(expected_attempts)
    ):
        findings.error(
            f"{context}: every preregistered control must succeed"
        )
    return control_entries, successful_rows


def validate_selection(
    config: dict[str, Any],
    manifest: dict[str, Any],
    recipe: dict[str, Any],
    selection_result: dict[str, Any],
    entries: list[dict[str, Any]],
    selection_ledger_path: Path,
    selection_result_path: Path,
    recipe_path: Path,
    config_path: Path,
    preregistration_path: Path,
    catalog_path: Path,
    manifest_path: Path,
    curve_validation_path: Path,
    dataset_validation_path: Path,
    findings: Findings,
) -> dict[str, Any]:
    if selection_result.get("result_payload_sha256") != payload_hash(
        selection_result, "result_payload_sha256"
    ):
        findings.error("selection result payload hash mismatch")
    if recipe.get("recipe_payload_sha256") != payload_hash(
        recipe, "recipe_payload_sha256"
    ):
        findings.error("frozen recipe payload hash mismatch")
    ledger_sha = sha256_file(selection_ledger_path)
    recipe_sha = sha256_file(recipe_path)
    for context, value in (
        ("recipe selection ledger", recipe.get("selection_ledger_sha256")),
        (
            "selection result selection ledger",
            selection_result.get("selection_ledger_sha256"),
        ),
    ):
        if value != ledger_sha:
            findings.error(f"{context} hash mismatch")
    if recipe.get("selection_result_sha256") != sha256_file(
        selection_result_path
    ):
        findings.error("frozen recipe selection-result file hash mismatch")
    if recipe.get(
        "selection_result_payload_sha256"
    ) != selection_result.get("result_payload_sha256"):
        findings.error("frozen recipe selection-result payload hash mismatch")
    for field, path in (
        ("config_sha256", config_path),
        ("preregistration_sha256", preregistration_path),
        ("catalog_sha256", catalog_path),
        ("manifest_sha256", manifest_path),
        ("curve_validation_sha256", curve_validation_path),
        ("dataset_validation_sha256", dataset_validation_path),
    ):
        if recipe.get(field) != sha256_file(path):
            findings.error(f"frozen recipe {field} mismatch")
    if recipe.get("experiment_id") != config.get("experiment_id"):
        findings.error("frozen recipe experiment id mismatch")
    if selection_result.get("experiment_id") != config.get("experiment_id"):
        findings.error("selection result experiment id mismatch")
    if selection_result.get("stage") != "selection_complete_blind_unopened":
        findings.error("selection result does not record blind-unopened stage")
    if recipe.get("freeze_stage") != (
        "committed_before_any_blind_curve_evaluation"
    ):
        findings.error("frozen recipe has an unexpected freeze stage")
    if recipe.get("native_research_engine_outcome", False) is not False:
        findings.error("frozen recipe claims a native Research Engine outcome")
    if selection_result.get("native_research_engine_outcome") is not False:
        findings.error("selection result claims a native Research Engine outcome")
    configured = {item["id"]: item for item in config["architectures"]}
    architecture = recipe.get("architecture")
    if (
        not isinstance(architecture, dict)
        or configured.get(architecture.get("id")) != architecture
    ):
        findings.error("frozen architecture is not an exact configured recipe")

    statuses = [item.get("status") for item in entries]
    if any(status not in {"success", "failed"} for status in statuses):
        findings.error("selection ledger contains an invalid status")
    stage_rank = {
        "screen": 0,
        "confirmation": 1,
        "frozen_reference_after_null": 1,
    }
    order = [
        2
        if str(item.get("stage", "")).startswith("control/")
        else stage_rank.get(str(item.get("stage", "")), 3)
        for item in entries
    ]
    if order != sorted(order):
        findings.error(
            "selection ledger order is not screen, confirmation, then controls"
        )
    if any(value == 3 for value in order):
        findings.error("selection ledger contains an unknown stage")
    observed_counts = ledger_counts(entries, "selection")
    compare_values(
        findings,
        "recipe.selection_run_counts",
        observed_counts,
        recipe.get("selection_run_counts"),
        absolute_tolerance=0.0,
        relative_tolerance=0.0,
    )
    compare_values(
        findings,
        "selection_result.run_counts",
        observed_counts,
        selection_result.get("run_counts"),
        absolute_tolerance=0.0,
        relative_tolerance=0.0,
    )
    if observed_counts["failed"] != 0:
        findings.error("selection ledger contains a failed required fit")
    if observed_counts["successful"] != len(entries):
        findings.error("selection ledger is not a complete success matrix")
    expected_screen = (
        len(config["selection_field_bits"])
        * len(config["architectures"])
        * len(config["seeds"])
    )
    if observed_counts["screen"] != expected_screen:
        findings.error(
            f"selection screen count {observed_counts['screen']} != {expected_screen}"
        )
    screen_rows = [
        item
        for item in entries
        if item.get("stage") == "screen" and item.get("status") == "success"
    ]
    for row in screen_rows:
        base = configured.get(str(row.get("architecture_id")))
        if base is None:
            findings.error("successful screen row uses an unknown architecture")
            continue
        staged = architecture_for_stage(base, config, "screen")
        validate_successful_fit_metadata(
            row,
            staged,
            staged["feature_mode"],
            findings,
            (
                f"screen {row.get('field_bits')}/"
                f"{row.get('architecture_id')}/{row.get('seed')}"
            ),
        )
    scores = architecture_scores(
        screen_rows, list(config["selection"]["primary_splits"])
    )
    if not scores:
        findings.error("selection ledger has no successful screen architecture")
        return {
            "selection_result_sha256": sha256_file(selection_result_path),
            "selection_ledger_sha256": ledger_sha,
            "recipe_sha256": recipe_sha,
            "run_counts": observed_counts,
        }
    compare_values(
        findings,
        "recipe.architecture_scores",
        scores,
        recipe.get("architecture_scores"),
        absolute_tolerance=1e-12,
        relative_tolerance=1e-12,
    )
    compare_values(
        findings,
        "selection_result.architecture_scores",
        scores,
        selection_result.get("architecture_scores"),
        absolute_tolerance=1e-12,
        relative_tolerance=1e-12,
    )
    screen_winner = scores[0]["architecture_id"]
    if recipe.get("screen_winner_architecture_id") != screen_winner:
        findings.error("frozen recipe screen winner is not ledger-derived")
    if selection_result.get("screen_winner_architecture_id") != screen_winner:
        findings.error("selection result screen winner is not ledger-derived")
    gate = corrected_transfer_gate(
        screen_rows,
        screen_winner,
        list(config["selection"]["primary_splits"]),
        float(config["selection"]["positive_familywise_alpha"]),
    )
    compare_values(
        findings,
        "recipe.screen_gate",
        gate,
        recipe.get("screen_gate"),
        absolute_tolerance=1e-12,
        relative_tolerance=1e-12,
    )
    compare_values(
        findings,
        "selection_result.screen_gate",
        gate,
        selection_result.get("screen_gate"),
        absolute_tolerance=1e-12,
        relative_tolerance=1e-12,
    )
    expected_confirmation_ids = [
        item["architecture_id"]
        for item in scores[
            : int(config["selection"]["top_confirmation_recipes"])
        ]
    ]
    if recipe.get("confirmation_architecture_ids") != expected_confirmation_ids:
        findings.error("confirmation recipe set is not ledger-derived")
    if (
        selection_result.get("confirmation_architecture_ids")
        != expected_confirmation_ids
    ):
        findings.error("selection result confirmation set is not ledger-derived")
    expected_confirmation = (
        len(config["confirmation_field_bits"])
        * len(expected_confirmation_ids)
        * len(config["seeds"])
    )
    if observed_counts["confirmation"] != expected_confirmation:
        findings.error(
            "selection confirmation count "
            f"{observed_counts['confirmation']} != {expected_confirmation}"
        )
    confirmation_rows = [
        item
        for item in entries
        if item.get("stage") in {
            "confirmation",
            "frozen_reference_after_null",
        }
        and item.get("status") == "success"
    ]
    expected_confirmation_stage = (
        "confirmation" if gate["pass"] else "frozen_reference_after_null"
    )
    for row in confirmation_rows:
        if row.get("stage") != expected_confirmation_stage:
            findings.error(
                "successful confirmation stage disagrees with the screen gate"
            )
        base = configured.get(str(row.get("architecture_id")))
        if base is None:
            findings.error(
                "successful confirmation row uses an unknown architecture"
            )
            continue
        staged = architecture_for_stage(base, config, "confirmation")
        validate_successful_fit_metadata(
            row,
            staged,
            staged["feature_mode"],
            findings,
            (
                f"confirmation {row.get('field_bits')}/"
                f"{row.get('architecture_id')}/{row.get('seed')}"
            ),
        )
    final_id = screen_winner
    if not isinstance(architecture, dict) or architecture.get("id") != final_id:
        findings.error("frozen architecture is not the ledger-derived finalist")
    if selection_result.get("frozen_architecture") != architecture:
        findings.error("selection result finalist differs from frozen recipe")
    if recipe.get("adaptive_search_stopped") is not (not gate["pass"]):
        findings.error("adaptive-search stop flag disagrees with screen gate")
    if selection_result.get("adaptive_search_stopped") is not (not gate["pass"]):
        findings.error("selection-result stop flag disagrees with screen gate")

    expected_screen_attempts = {
        (int(bits), item["id"], int(seed))
        for bits in config["selection_field_bits"]
        for item in config["architectures"]
        for seed in config["seeds"]
    }
    observed_screen_attempts = {
        (
            int(item.get("field_bits", -1)),
            str(item.get("architecture_id")),
            int(item.get("seed", -1)),
        )
        for item in entries
        if item.get("stage") == "screen"
    }
    if observed_screen_attempts != expected_screen_attempts:
        findings.error("selection screen attempt matrix is incomplete or unexpected")
    expected_confirmation_attempts = {
        (int(bits), architecture_id, int(seed))
        for bits in config["confirmation_field_bits"]
        for architecture_id in expected_confirmation_ids
        for seed in config["seeds"]
    }
    observed_confirmation_attempts = {
        (
            int(item.get("field_bits", -1)),
            str(item.get("architecture_id")),
            int(item.get("seed", -1)),
        )
        for item in entries
        if item.get("stage")
        in {"confirmation", "frozen_reference_after_null"}
    }
    if observed_confirmation_attempts != expected_confirmation_attempts:
        findings.error(
            "selection confirmation attempt matrix is incomplete or unexpected"
        )
    if len(observed_screen_attempts) != observed_counts["screen"]:
        findings.error("selection screen ledger has duplicate attempt identities")
    if (
        len(observed_confirmation_attempts)
        != observed_counts["confirmation"]
    ):
        findings.error("selection confirmation ledger has duplicate attempts")

    control_entries, successful_control_rows = validate_control_attempt_matrix(
        config,
        configured[final_id],
        entries,
        findings,
        "selection",
    )
    if observed_counts["controls"] != len(control_entries):
        findings.error("selection control count differs from control ledger")
    selection_controls = selection_result.get("controls")
    if not isinstance(selection_controls, dict):
        findings.error("selection result controls must be an object")
        selection_controls = {}
    reported_control_rows = selection_controls.get("runs")
    if not isinstance(reported_control_rows, list):
        findings.error("selection result control runs must be an array")
        reported_control_rows = []
    if canonical_json(reported_control_rows) != canonical_json(
        successful_control_rows
    ):
        findings.error("selection control rows differ from selection ledger")
    control_decision = recompute_control_decision(
        reported_control_rows,
        list(config["selection"]["primary_splits"]),
        str(config["controls"]["canary_architecture_id"]),
        findings,
        "selection",
    )
    for key, value in control_decision.items():
        if selection_controls.get(key) != value:
            findings.error(
                f"selection controls.{key} disagrees with recomputed logic"
            )
    expected_recipe_control_summary = {
        key: control_decision[key]
        for key in (
            "pipeline_valid",
            "complete_matrix",
            "canary_pass",
            "negative_pass",
        )
    }
    if recipe.get("controls_summary") != expected_recipe_control_summary:
        findings.error("recipe control summary is not selection-ledger-derived")
    authorized = bool(control_decision["pipeline_valid"])
    if selection_result.get("blind_evaluation_authorized") is not authorized:
        findings.error("selection blind authorization disagrees with controls")
    if recipe.get("blind_evaluation_authorized") is not authorized:
        findings.error("recipe blind authorization disagrees with controls")
    if not authorized:
        findings.error("blind evaluation was not authorized by selection controls")

    opened = selection_result.get("dataset_files_opened")
    if opened != recipe.get("dataset_files_opened"):
        findings.error("selection result and recipe opened-file lists differ")
    development_bits = {
        int(value)
        for value in (
            list(config["selection_field_bits"])
            + list(config["confirmation_field_bits"])
            + list(CONTROL_FIELD_BITS)
        )
    }
    expected_opened = sorted(
        {
            Path(str(entry["relative_path"])).name
            for entry in manifest.get("files", [])
            if int(entry.get("field_bits", -1)) in development_bits
            and entry.get("scope") == "development"
        }
    )
    if opened != expected_opened:
        findings.error("selection opened-file list differs from development shards")
    if selection_result.get("blind_dataset_shard_opened") is not False:
        findings.error("selection result says a blind shard was opened")
    if recipe.get("blind_dataset_shard_opened") is not False:
        findings.error("recipe says a blind shard was opened")
    if isinstance(opened, list) and any(
        "blind" in str(path).lower() for path in opened
    ):
        findings.error("selection opened-file list contains a blind shard")
    return {
        "selection_result_sha256": sha256_file(selection_result_path),
        "selection_ledger_sha256": ledger_sha,
        "recipe_sha256": recipe_sha,
        "recipe_payload_sha256": recipe.get("recipe_payload_sha256"),
        "screen_winner_architecture_id": screen_winner,
        "final_architecture_id": final_id,
        "screen_gate_pass": gate["pass"],
        "blind_evaluation_authorized": authorized,
        "control_attempts": len(control_entries),
        "run_counts": observed_counts,
    }


def validate_control_summary(
    selection_result: dict[str, Any],
    assay_result: dict[str, Any],
    findings: Findings,
) -> dict[str, Any]:
    controls = assay_result.get("controls")
    selection_controls = selection_result.get("controls")
    if not isinstance(controls, dict):
        findings.error("assay result controls must be an object")
        return {}
    if not isinstance(selection_controls, dict):
        findings.error("selection result controls must be an object")
        return {}
    if canonical_json(controls) != canonical_json(selection_controls):
        findings.error(
            "assay controls differ from the frozen selection result"
        )
    reported_rows = controls.get("runs")
    if not isinstance(reported_rows, list):
        findings.error("assay result control runs must be an array")
        return {}
    return {
        "pipeline_valid": controls.get("pipeline_valid"),
        "complete_matrix": controls.get("complete_matrix"),
        "canary_pass": controls.get("canary_pass"),
        "negative_pass": controls.get("negative_pass"),
        "attempts": len(CONTROL_FIELD_BITS) * len(CONTROL_IDS),
        "successful": len(reported_rows),
        "metric_replay_scope": (
            "selection-ledger binding and decision logic; controls are copied "
            "unchanged into the assay result"
        ),
    }


def validate_evaluation_ledger(
    config: dict[str, Any],
    recipe: dict[str, Any],
    assay_result: dict[str, Any],
    entries: list[dict[str, Any]],
    evaluation_ledger_path: Path,
    findings: Findings,
) -> dict[str, Any]:
    if assay_result.get("evaluation_ledger_sha256") != sha256_file(
        evaluation_ledger_path
    ):
        findings.error("evaluation ledger hash mismatch")
    statuses = [item.get("status") for item in entries]
    if any(status not in {"success", "failed"} for status in statuses):
        findings.error("evaluation ledger contains an invalid status")
    if any(item.get("stage") != "frozen_ladder" for item in entries):
        findings.error("evaluation ledger contains a non-frozen stage")
    observed_counts = ledger_counts(entries, "evaluation")
    compare_values(
        findings,
        "assay_result.run_counts",
        observed_counts,
        assay_result.get("run_counts"),
        absolute_tolerance=0.0,
        relative_tolerance=0.0,
    )
    if observed_counts["failed"] != 0:
        findings.error("evaluation ledger contains a failed frozen fit")
    if observed_counts["successful"] != len(entries):
        findings.error("evaluation ledger is not a complete success matrix")
    expected_frozen = len(config["field_bits"]) * len(config["seeds"])
    if observed_counts["frozen"] != expected_frozen:
        findings.error(
            f"frozen fit count {observed_counts['frozen']} != {expected_frozen}"
        )
    expected_frozen_attempts = {
        (int(bits), int(seed))
        for bits in config["field_bits"]
        for seed in config["seeds"]
    }
    observed_frozen_attempts = {
        (int(row.get("field_bits", -1)), int(row.get("seed", -1)))
        for row in entries
        if row.get("stage") == "frozen_ladder"
    }
    if observed_frozen_attempts != expected_frozen_attempts:
        findings.error("frozen evaluation attempt matrix is incomplete")
    if len(observed_frozen_attempts) != observed_counts["frozen"]:
        findings.error("frozen evaluation ledger has duplicate attempts")
    final_architecture = recipe.get("architecture")
    if not isinstance(final_architecture, dict) or "id" not in final_architecture:
        findings.error("evaluation recipe has no frozen architecture")
        return observed_counts
    final_id = final_architecture["id"]
    for row in entries:
        if row.get("architecture_id") != final_id:
            findings.error("frozen evaluation used a non-frozen architecture")
        if row.get("status") != "success":
            continue
        bits = int(row.get("field_bits", -1))
        stage = (
            "frozen_blind"
            if bits in {int(value) for value in config["blind_field_bits"]}
            else "confirmation"
        )
        staged = architecture_for_stage(final_architecture, config, stage)
        validate_successful_fit_metadata(
            row,
            staged,
            staged["feature_mode"],
            findings,
            f"frozen evaluation {bits}/{row.get('seed')}",
        )
    return observed_counts


def validate_input_validation_reports(
    config: dict[str, Any],
    preregistration: dict[str, Any],
    catalog: dict[str, Any],
    manifest: dict[str, Any],
    curve_validation: dict[str, Any],
    dataset_validation: dict[str, Any],
    config_path: Path,
    catalog_path: Path,
    manifest_path: Path,
    curve_validation_path: Path,
    dataset_validation_path: Path,
    findings: Findings,
) -> dict[str, Any]:
    config_sha = sha256_file(config_path)
    catalog_sha = sha256_file(catalog_path)
    manifest_sha = sha256_file(manifest_path)
    oracle_sha = sha256_file(ROOT / "experiments/framework/ec_oracle.py")
    if preregistration.get("status") != (
        "catalog_and_dataset_validated_selection_authorized"
    ):
        findings.error("preregistration status does not authorize selection")
    if preregistration.get("authorized_field_bits") != config.get("field_bits"):
        findings.error("preregistration field ladder differs from configuration")
    if catalog.get("source_worktree_dirty") is not False:
        findings.error("curve catalog was generated from a dirty worktree")
    if not git_commit_exists(catalog.get("source_commit")):
        findings.error("curve catalog source commit does not resolve")
    if curve_validation.get("status") != "pass":
        findings.error("independent curve validation did not pass")
    if curve_validation.get("producer_imported") is not False:
        findings.error("curve validation imported its producer")
    if curve_validation.get("catalog_sha256") != catalog_sha:
        findings.error("curve validation catalog hash mismatch")
    if curve_validation.get("validator_sha256") != sha256_file(
        ROOT
        / "experiments/ml_structure_probe/p1_toy_scaling/validate_curves.py"
    ):
        findings.error("curve validation source hash mismatch")
    if curve_validation.get("oracle_sha256") != oracle_sha:
        findings.error("curve validation oracle hash mismatch")
    if int(curve_validation.get("curve_count", -1)) != int(
        catalog.get("curve_count", -2)
    ):
        findings.error("curve validation curve count mismatch")
    if curve_validation.get("errors") != []:
        findings.error("curve validation reports errors")

    if dataset_validation.get("status") != "pass":
        findings.error("independent dataset validation did not pass")
    if dataset_validation.get("producer_imported") is not False:
        findings.error("dataset validation imported its producer")
    if dataset_validation.get("manifest_sha256") != manifest_sha:
        findings.error("dataset validation manifest hash mismatch")
    if dataset_validation.get("validator_sha256") != sha256_file(
        ROOT
        / "experiments/ml_structure_probe/p1_toy_scaling/validate_dataset.py"
    ):
        findings.error("dataset validation source hash mismatch")
    if dataset_validation.get("oracle_sha256") != oracle_sha:
        findings.error("dataset validation oracle hash mismatch")
    expected_records = int(manifest.get("records", -1))
    if dataset_validation.get("full_ec_replay") is not True:
        findings.error("dataset validation did not perform full EC replay")
    if int(dataset_validation.get("ec_checks", -1)) != expected_records:
        findings.error("dataset validation EC replay count mismatch")
    if int(dataset_validation.get("records", -1)) != expected_records:
        findings.error("dataset validation record count mismatch")
    if dataset_validation.get("errors") != []:
        findings.error("dataset validation reports errors")
    expected_bindings = {
        "source_commit": catalog.get("source_commit"),
        "config_sha256": config_sha,
        "catalog_file_sha256": catalog_sha,
        "catalog_payload_sha256": catalog.get("catalog_sha256"),
        "manifest_file_sha256": manifest_sha,
        "manifest_payload_sha256": manifest.get("manifest_sha256"),
        "curve_validation_sha256": sha256_file(curve_validation_path),
        "dataset_validation_sha256": sha256_file(dataset_validation_path),
        "dataset_records": expected_records,
        "full_ec_replay": True,
    }
    if preregistration.get("frozen_bindings") != expected_bindings:
        findings.error("preregistration frozen bindings mismatch")
    return {
        "curve_validation_status": curve_validation.get("status"),
        "curve_validation_sha256": sha256_file(curve_validation_path),
        "curve_count": curve_validation.get("curve_count"),
        "dataset_validation_status": dataset_validation.get("status"),
        "dataset_validation_sha256": sha256_file(dataset_validation_path),
        "dataset_full_ec_replay": dataset_validation.get("full_ec_replay"),
        "dataset_ec_checks": dataset_validation.get("ec_checks"),
    }


def validate_dataset_bindings(
    config: dict[str, Any],
    catalog: dict[str, Any],
    manifest: dict[str, Any],
    config_path: Path,
    catalog_path: Path,
    manifest_path: Path,
    dataset_dir: Path,
    findings: Findings,
) -> dict[int, dict[str, np.ndarray]]:
    if catalog.get("config_sha256") != sha256_file(config_path):
        findings.error("catalog/config hash mismatch")
    if catalog.get("catalog_sha256") != payload_hash(
        catalog, "catalog_sha256"
    ):
        findings.error("catalog payload hash mismatch")
    if manifest.get("config_sha256") != sha256_file(config_path):
        findings.error("manifest/config hash mismatch")
    if manifest.get("catalog_sha256") != sha256_file(catalog_path):
        findings.error("manifest/catalog hash mismatch")
    if manifest.get("catalog_payload_sha256") != catalog.get("catalog_sha256"):
        findings.error("manifest/catalog payload hash mismatch")
    if manifest.get("manifest_sha256") != payload_hash(
        manifest, "manifest_sha256"
    ):
        findings.error("manifest payload hash mismatch")
    if manifest.get("experiment_id") != config.get("experiment_id"):
        findings.error("manifest experiment id mismatch")
    if catalog.get("experiment_id") != config.get("experiment_id"):
        findings.error("catalog experiment id mismatch")
    files = manifest.get("files")
    if not isinstance(files, list):
        findings.error("manifest files must be an array")
        return {}
    by_bits: dict[int, dict[str, np.ndarray]] = {}
    split_codes = manifest.get("split_codes")
    if not isinstance(split_codes, dict):
        findings.error("manifest split_codes must be an object")
        return {}
    expected_split_names = {"train", *SPLIT_NAMES}
    if set(split_codes) != expected_split_names:
        findings.error(
            "manifest split names differ from the preregistered split set"
        )
    if len({int(value) for value in split_codes.values()}) != len(split_codes):
        findings.error("manifest split codes are not unique")
    observed_total = 0
    observed_split_totals = {name: 0 for name in split_codes}
    file_keys: list[tuple[int, str]] = []
    split_parts: dict[int, dict[str, list[np.ndarray]]] = {}
    for entry in files:
        try:
            bits = int(entry["field_bits"])
            scope = str(entry["scope"])
            path = safe_child(dataset_dir, entry["relative_path"], findings)
            if path is None or not path.is_file():
                findings.error(
                    f"missing {scope} dataset file for {bits} bits"
                )
                continue
            if sha256_file(path) != entry["sha256"]:
                findings.error(
                    f"{scope} dataset file hash mismatch for {bits} bits"
                )
                continue
            records = np.load(path, mmap_mode="r", allow_pickle=False)
        except (KeyError, OSError, TypeError, ValueError) as error:
            findings.error(f"cannot load dataset entry: {error}")
            continue
        file_keys.append((bits, scope))
        if records.dtype.names is None:
            findings.error(f"{bits}-bit dataset does not have a structured dtype")
            continue
        missing_fields = REQUIRED_RECORD_FIELDS - set(records.dtype.names)
        if missing_fields:
            findings.error(
                f"{bits}-bit dataset misses fields {sorted(missing_fields)}"
            )
            continue
        normalized_dtype = json.loads(json.dumps(records.dtype.descr))
        if normalized_dtype != manifest.get("dtype"):
            findings.error(f"{bits}-bit {scope} dataset dtype mismatch")
        if len(records) != int(entry.get("records", -1)):
            findings.error(
                f"{bits}-bit {scope} dataset record count mismatch"
            )
        if path.stat().st_size != int(entry.get("bytes", -1)):
            findings.error(f"{bits}-bit {scope} dataset byte count mismatch")
        if np.any(records["field_p"] < (1 << (bits - 1))) or np.any(
            records["field_p"] >= (1 << bits)
        ):
            findings.error(f"{bits}-bit {scope} dataset field width mismatch")
        if np.any(records["scalar"] == 0) or np.any(
            records["scalar"] >= records["group_order"]
        ):
            findings.error(f"{bits}-bit {scope} dataset scalar range mismatch")
        known_codes = np.asarray(
            [int(value) for value in split_codes.values()],
            dtype=records["split_code"].dtype,
        )
        if np.any(~np.isin(records["split_code"], known_codes)):
            findings.error(f"{bits}-bit {scope} dataset has unknown split codes")
        observed_total += len(records)
        per_bits = split_parts.setdefault(
            bits, {name: [] for name in split_codes}
        )
        scoped_counts: dict[str, int] = {}
        for name, code in split_codes.items():
            selected = np.asarray(
                records[records["split_code"] == int(code)]
            )
            scoped_counts[name] = len(selected)
            expected = int(entry.get("split_counts", {}).get(name, -1))
            if len(selected) != expected:
                findings.error(
                    f"{bits}-bit {scope} split count mismatch for {name}"
                )
            observed_split_totals[name] += len(selected)
            if len(selected):
                per_bits[name].append(selected)
        blind_count = scoped_counts.get("blind_curve_blind_generator", 0)
        nonblind_count = sum(scoped_counts.values()) - blind_count
        if scope == "development" and blind_count:
            findings.error(
                f"{bits}-bit development shard contains blind records"
            )
        if scope == "blind" and nonblind_count:
            findings.error(f"{bits}-bit blind shard contains development records")
    expected_bits = {int(value) for value in config["field_bits"]}
    expected_file_keys = {
        (bits, scope)
        for bits in expected_bits
        for scope in ("development", "blind")
    }
    if set(file_keys) != expected_file_keys:
        findings.error("dataset shard matrix differs from configuration")
    if len(file_keys) != len(expected_file_keys):
        findings.error("dataset manifest has duplicate shard identities")
    for bits in expected_bits:
        per_bits = split_parts.get(bits, {})
        split_records: dict[str, np.ndarray] = {}
        for name in split_codes:
            parts = per_bits.get(name, [])
            if not parts:
                split_records[name] = np.empty(
                    0,
                    dtype=np.dtype(
                        [
                            tuple(item)
                            for item in manifest.get("dtype", [])
                        ]
                    ),
                )
            elif len(parts) == 1:
                split_records[name] = parts[0]
            else:
                split_records[name] = np.concatenate(parts)
        by_bits[bits] = split_records
    if observed_total != int(manifest.get("records", -1)):
        findings.error("manifest total record count mismatch")
    for name, count in observed_split_totals.items():
        if count != int(manifest.get("split_counts", {}).get(name, -1)):
            findings.error(f"manifest aggregate split count mismatch for {name}")
    return by_bits


def validate_raw_predictions(
    config: dict[str, Any],
    assay_result: dict[str, Any],
    recipe: dict[str, Any],
    datasets: dict[int, dict[str, np.ndarray]],
    raw_dir: Path,
    evaluation_entries: list[dict[str, Any]],
    findings: Findings,
) -> tuple[list[dict[str, Any]], OracleAudit]:
    artifacts = assay_result.get("raw_prediction_artifacts")
    if not isinstance(artifacts, list):
        findings.error("raw_prediction_artifacts must be an array")
        return [], OracleAudit(findings)
    ladder = assay_result.get("frozen_ladder")
    if not isinstance(ladder, list):
        findings.error("frozen_ladder must be an array")
        return [], OracleAudit(findings)
    ladder_index = {
        int(row["field_bits"]): row
        for row in ladder
        if isinstance(row, dict) and "field_bits" in row
    }
    artifact_index = {
        int(row["field_bits"]): row
        for row in artifacts
        if isinstance(row, dict) and "field_bits" in row
    }
    expected_bits = {int(value) for value in config["field_bits"]}
    if set(ladder_index) != expected_bits:
        findings.error("frozen ladder field-size set is incomplete")
    if set(artifact_index) != expected_bits:
        findings.error("raw prediction artifact field-size set is incomplete")
    if len(ladder) != len(ladder_index):
        findings.error("frozen ladder contains duplicate field-size rows")
    if len(artifacts) != len(artifact_index):
        findings.error("raw prediction list contains duplicate field-size rows")
    recovery_widths = [int(value) for value in config["recovery"]["beam_widths"]]
    oracle = OracleAudit(findings)
    validation_rows: list[dict[str, Any]] = []
    for bits in sorted(expected_bits):
        dataset = datasets.get(bits)
        artifact = artifact_index.get(bits)
        reported = ladder_index.get(bits)
        if dataset is None or artifact is None or reported is None:
            continue
        path = safe_child(raw_dir, artifact.get("path"), findings)
        if path is None or not path.is_file():
            findings.error(f"missing raw prediction artifact for {bits} bits")
            continue
        if sha256_file(path) != artifact.get("sha256"):
            findings.error(f"raw prediction hash mismatch for {bits} bits")
            continue
        try:
            with np.load(path, allow_pickle=False) as archive:
                raw_records = np.asarray(archive["records"])
                probabilities = np.asarray(archive["probabilities"])
                raw_split_names = tuple(str(value) for value in archive["split_names"])
        except (KeyError, OSError, ValueError) as error:
            findings.error(f"cannot load {bits}-bit raw predictions: {error}")
            continue
        if raw_split_names != SPLIT_NAMES:
            findings.error(f"{bits}-bit raw split order is not preregistered")
            continue
        expected_records = np.concatenate(
            [dataset[name] for name in SPLIT_NAMES]
        )
        if not np.array_equal(raw_records, expected_records):
            findings.error(
                f"{bits}-bit raw prediction records differ from dataset"
            )
            continue
        if probabilities.shape != (len(raw_records), bits):
            findings.error(
                f"{bits}-bit probability shape {probabilities.shape} is invalid"
            )
            continue
        if not np.isfinite(probabilities).all():
            findings.error(f"{bits}-bit probabilities contain non-finite values")
            continue
        if np.any(probabilities < 0.0) or np.any(probabilities > 1.0):
            findings.error(f"{bits}-bit probabilities lie outside [0,1]")
            continue
        if len(raw_records) != int(artifact.get("records", -1)):
            findings.error(f"{bits}-bit raw artifact record count mismatch")
        offset = 0
        metric_rows: dict[str, Any] = {}
        recovery_rows: dict[str, Any] = {}
        for split in SPLIT_NAMES:
            records = dataset[split]
            split_probabilities = probabilities[offset : offset + len(records)]
            offset += len(records)
            metrics, recovery = recompute_metrics(
                records,
                split_probabilities,
                public_uniform_scalar_prior(records, bits),
                recovery_widths,
                oracle,
                findings,
                f"{bits}/{split}",
            )
            metric_rows[split] = metrics
            recovery_rows[split] = recovery
            compare_values(
                findings,
                f"frozen_ladder[{bits}].metrics.{split}",
                metrics,
                reported.get("metrics", {}).get(split),
            )
        if offset != len(probabilities):
            findings.error(f"{bits}-bit raw split offsets do not consume artifact")
        successful_fit_rows = [
            row
            for row in evaluation_entries
            if row.get("stage") == "frozen_ladder"
            and int(row.get("field_bits", -1)) == bits
            and row.get("status") == "success"
        ]
        if int(reported.get("successful_seed_fits", -1)) != len(
            successful_fit_rows
        ):
            findings.error(f"{bits}-bit successful seed fit count mismatch")
        expected_fit_seconds = sum(
            float(row["fit_seconds"]) for row in successful_fit_rows
        )
        if not math.isclose(
            float(reported.get("fit_seconds_total", -1)),
            expected_fit_seconds,
            rel_tol=1e-12,
            abs_tol=1e-12,
        ):
            findings.error(f"{bits}-bit total fit time differs from ledger")
        if successful_fit_rows:
            expected_model_bytes = float(
                statistics.median(
                    int(row["model_bytes_pickle"])
                    for row in successful_fit_rows
                )
            )
            if not math.isclose(
                float(reported.get("model_bytes_median", -1)),
                expected_model_bytes,
                rel_tol=0.0,
                abs_tol=0.0,
            ):
                findings.error(
                    f"{bits}-bit median model bytes differs from ledger"
                )
        validation_rows.append(
            {
                "field_bits": bits,
                "artifact_sha256": sha256_file(path),
                "records": len(raw_records),
                "metrics_recomputed": metric_rows,
                "candidate_recovery": recovery_rows,
            }
        )
    return validation_rows, oracle


def validate_solver_baselines(
    config: dict[str, Any],
    assay_result: dict[str, Any],
    datasets: dict[int, dict[str, np.ndarray]],
    oracle: OracleAudit,
    findings: Findings,
) -> list[dict[str, Any]]:
    rows = assay_result.get("solver_baselines")
    if not isinstance(rows, list):
        findings.error("solver_baselines must be an array")
        return []
    indexed = {
        (int(row["field_bits"]), str(row["method"])): row
        for row in rows
        if isinstance(row, dict)
        and "field_bits" in row
        and "method" in row
    }
    expected_keys = {
        (int(bits), method)
        for bits in config["field_bits"]
        for method in ("bsgs", "pollard_rho")
    }
    if set(indexed) != expected_keys:
        findings.error("solver baseline matrix is incomplete or unexpected")
    if len(rows) != len(indexed):
        findings.error("solver baselines contain duplicate identities")
    target_limit = int(
        config["recovery"]["maximum_bsgs_targets_per_split"]
    )
    validation: list[dict[str, Any]] = []
    for key in sorted(expected_keys):
        bits, method = key
        reported = indexed.get(key)
        dataset = datasets.get(bits)
        if reported is None or dataset is None:
            continue
        records = dataset.get("blind_curve_blind_generator")
        if records is None or not len(records):
            findings.error(f"{bits}/{method}: blind baseline split is empty")
            continue
        expected_indices = np.linspace(
            0,
            len(records) - 1,
            min(target_limit, len(records)),
            dtype=np.int64,
        )
        runs = reported.get("runs")
        if not isinstance(runs, list):
            findings.error(f"{bits}/{method}: baseline runs must be an array")
            continue
        if len(runs) != len(expected_indices):
            findings.error(f"{bits}/{method}: baseline target count mismatch")
        successes = 0
        operations: list[int] = []
        wall_times: list[float] = []
        memory: list[int] = []
        candidate_checks = 0
        for ordinal, index_raw in enumerate(expected_indices):
            if ordinal >= len(runs):
                break
            run = runs[ordinal]
            if not isinstance(run, dict):
                findings.error(
                    f"{bits}/{method}: baseline run {ordinal} is not an object"
                )
                continue
            index = int(index_raw)
            record = records[index]
            expected_identity = {
                "sample_ordinal": ordinal,
                "record_index": index,
                "curve_index": int(record["curve_index"]),
                "generator_index": int(record["generator_index"]),
                "expected_scalar": int(record["scalar"]),
            }
            for field, value in expected_identity.items():
                if run.get(field) != value:
                    findings.error(
                        f"{bits}/{method}/{ordinal}: {field} differs "
                        "from the selected blind record"
                    )
            candidate = run.get("candidate_scalar")
            recovered = False
            if candidate is not None:
                if isinstance(candidate, bool) or not isinstance(candidate, int):
                    findings.error(
                        f"{bits}/{method}/{ordinal}: candidate is not an integer"
                    )
                else:
                    candidate_checks += 1
                    recovered = oracle.check(record, candidate)
                    if recovered != (candidate == int(record["scalar"])):
                        findings.error(
                            f"{bits}/{method}/{ordinal}: candidate label and "
                            "EC replay disagree"
                        )
            successes += int(recovered)
            try:
                operation_count = int(run["group_operations"])
                wall_time = float(run["wall_time_seconds"])
                memory_bytes = int(run["memory_bytes"])
            except (KeyError, TypeError, ValueError):
                findings.error(
                    f"{bits}/{method}/{ordinal}: malformed resource counters"
                )
                continue
            if operation_count < 0:
                findings.error(
                    f"{bits}/{method}/{ordinal}: negative operation count"
                )
            if not math.isfinite(wall_time) or wall_time < 0.0:
                findings.error(
                    f"{bits}/{method}/{ordinal}: invalid wall time"
                )
            if memory_bytes < 0:
                findings.error(f"{bits}/{method}/{ordinal}: negative memory")
            operations.append(operation_count)
            wall_times.append(wall_time)
            memory.append(memory_bytes)
        if operations and len(operations) == len(expected_indices):
            recomputed = {
                "field_bits": bits,
                "method": method,
                "targets": len(expected_indices),
                "successes": successes,
                "success_rate": successes / len(expected_indices),
                "median_group_operations": float(
                    statistics.median(operations)
                ),
                "median_wall_time_seconds": float(
                    statistics.median(wall_times)
                ),
                "peak_memory_bytes": int(max(memory)),
                "memory_is_estimate": True,
                "measurement_mode": (
                    "cold start; any table is rebuilt for every target"
                ),
                "precomputation_reusable_for_same_curve_generator": (
                    method == "bsgs"
                ),
                "runs": runs,
            }
            compare_values(
                findings,
                f"solver_baselines[{bits}/{method}]",
                recomputed,
                reported,
                absolute_tolerance=0.0,
                relative_tolerance=0.0,
            )
        validation.append(
            {
                "field_bits": bits,
                "method": method,
                "targets": len(expected_indices),
                "candidate_checks": candidate_checks,
                "ec_valid_recoveries": successes,
            }
        )
    return validation


def validate(
    *,
    config_path: Path,
    preregistration_path: Path,
    catalog_path: Path,
    manifest_path: Path,
    curve_validation_path: Path,
    dataset_validation_path: Path,
    dataset_dir: Path,
    selection_result_path: Path,
    selection_ledger_path: Path,
    recipe_path: Path,
    assay_result_path: Path,
    evaluation_ledger_path: Path,
    raw_dir: Path,
) -> dict[str, Any]:
    findings = Findings()
    started = time.perf_counter()
    config = load_json(config_path)
    preregistration = load_json(preregistration_path)
    catalog = load_json(catalog_path)
    manifest = load_json(manifest_path)
    curve_validation = load_json(curve_validation_path)
    dataset_validation = load_json(dataset_validation_path)
    selection_result = load_json(selection_result_path)
    recipe = load_json(recipe_path)
    assay_result = load_json(assay_result_path)
    selection_entries, _ = load_ledger(
        selection_ledger_path, findings, "selection ledger"
    )
    evaluation_entries, _ = load_ledger(
        evaluation_ledger_path, findings, "evaluation ledger"
    )

    experiment_id = config.get("experiment_id")
    for label, document in (
        ("preregistration", preregistration),
        ("catalog", catalog),
        ("manifest", manifest),
        ("curve validation", curve_validation),
        ("dataset validation", dataset_validation),
        ("selection result", selection_result),
        ("frozen recipe", recipe),
        ("assay result", assay_result),
    ):
        if document.get("experiment_id") != experiment_id:
            findings.error(f"{label} experiment id mismatch")
    if preregistration.get("native_research_engine_run") is not False:
        findings.error("preregistration does not preserve non-native scope")
    if preregistration.get("native_outcome_prohibited") is not True:
        findings.error("preregistration does not prohibit native outcomes")
    if config.get("native_research_engine_outcome") is not False:
        findings.error("configuration claims a native Research Engine outcome")
    selection_policy = config.get("selection", {})
    if (
        selection_policy.get("top_confirmation_recipes") != 1
        or selection_policy.get("confirmation_may_reselect_architecture")
        is not False
        or selection_policy.get(
            "architecture_identity_frozen_after_selection_sizes"
        )
        is not True
    ):
        findings.error("configuration architecture-freeze policy mismatch")
    if catalog.get("native_research_engine_outcome") is not False:
        findings.error("catalog claims a native Research Engine outcome")
    if assay_result.get("native_research_engine_outcome") is not False:
        findings.error("assay result claims a native Research Engine outcome")
    configured_bits = [int(value) for value in config.get("field_bits", [])]
    if configured_bits != [12, 16, 20, 24] or max(configured_bits, default=0) > 24:
        findings.error("configured field ladder differs from authorized 12/16/20/24")
    if preregistration.get("authorized_field_bits") != configured_bits:
        findings.error("preregistration/config field ladder mismatch")
    if config.get("deferred_field_bits") != [28, 32]:
        findings.error("configuration does not keep 28/32 deferred")
    if assay_result.get("deferred_field_bits") != [28, 32]:
        findings.error("assay result does not keep 28/32 deferred")
    if assay_result.get("classification") != config.get("classification"):
        findings.error("assay classification differs from configuration")
    expected_baseline = config.get("selection", {}).get("baseline")
    for label, document in (
        ("selection result", selection_result),
        ("frozen recipe", recipe),
        ("assay result", assay_result),
    ):
        if document.get("metric_baseline") != expected_baseline:
            findings.error(f"{label} metric baseline mismatch")
    expected_records = int(manifest.get("records", -1))
    for label, document in (
        ("selection result", selection_result),
        ("frozen recipe", recipe),
        ("assay result", assay_result),
    ):
        if document.get("dataset_records") != expected_records:
            findings.error(f"{label} dataset record count mismatch")
    expected_training_protocol = (
        "architecture frozen after 12/16 selection; retrained independently "
        "at each size; no cross-size weight transfer"
    )
    if recipe.get("training_protocol") != expected_training_protocol:
        findings.error("frozen recipe training protocol mismatch")
    if assay_result.get("training_protocol") != expected_training_protocol:
        findings.error("assay result training protocol mismatch")
    if assay_result.get("result_payload_sha256") != payload_hash(
        assay_result, "result_payload_sha256"
    ):
        findings.error("assay result payload hash mismatch")
    for field, path in (
        ("config_sha256", config_path),
        ("preregistration_sha256", preregistration_path),
        ("catalog_sha256", catalog_path),
        ("manifest_sha256", manifest_path),
        ("curve_validation_sha256", curve_validation_path),
        ("dataset_validation_sha256", dataset_validation_path),
    ):
        if assay_result.get(field) != sha256_file(path):
            findings.error(f"assay result {field} mismatch")
    recipe_sha = sha256_file(recipe_path)
    if assay_result.get("frozen_recipe_file_sha256") != recipe_sha:
        findings.error("assay result frozen recipe file hash mismatch")
    if assay_result.get(
        "frozen_recipe_payload_sha256"
    ) != recipe.get("recipe_payload_sha256"):
        findings.error("assay result frozen recipe payload hash mismatch")
    if assay_result.get("frozen_recipe") != recipe:
        findings.error("assay result embedded recipe differs from frozen file")
    if assay_result.get("selection_ledger_sha256") != sha256_file(
        selection_ledger_path
    ):
        findings.error("assay result selection ledger hash mismatch")
    if assay_result.get("selection_result_sha256") != sha256_file(
        selection_result_path
    ):
        findings.error("assay result selection-result file hash mismatch")
    if assay_result.get(
        "selection_result_payload_sha256"
    ) != selection_result.get("result_payload_sha256"):
        findings.error("assay result selection-result payload hash mismatch")
    if assay_result.get("selection_run_counts") != recipe.get(
        "selection_run_counts"
    ):
        findings.error("assay result selection counts differ from recipe")
    if assay_result.get("architecture_scores") != recipe.get(
        "architecture_scores"
    ):
        findings.error("assay result architecture scores differ from recipe")
    if assay_result.get("screen_gate") != recipe.get("screen_gate"):
        findings.error("assay result screen gate differs from recipe")
    environment = assay_result.get("environment")
    if not isinstance(environment, dict):
        findings.error("assay result environment must be an object")
    else:
        runtime_versions = recipe.get("runtime_versions", {})
        for name in ("numpy", "scipy", "sklearn"):
            if environment.get(name) != runtime_versions.get(name):
                findings.error(f"assay environment {name} version mismatch")
        jobs = environment.get("jobs")
        if (
            not isinstance(jobs, int)
            or isinstance(jobs, bool)
            or not 1 <= jobs <= int(config["budget"]["max_workers"])
        ):
            findings.error("assay environment worker count is invalid")

    selection_validation = validate_selection(
        config,
        manifest,
        recipe,
        selection_result,
        selection_entries,
        selection_ledger_path,
        selection_result_path,
        recipe_path,
        config_path,
        preregistration_path,
        catalog_path,
        manifest_path,
        curve_validation_path,
        dataset_validation_path,
        findings,
    )
    evaluation_counts = validate_evaluation_ledger(
        config,
        recipe,
        assay_result,
        evaluation_entries,
        evaluation_ledger_path,
        findings,
    )
    input_validation = validate_input_validation_reports(
        config,
        preregistration,
        catalog,
        manifest,
        curve_validation,
        dataset_validation,
        config_path,
        catalog_path,
        manifest_path,
        curve_validation_path,
        dataset_validation_path,
        findings,
    )
    datasets = validate_dataset_bindings(
        config,
        catalog,
        manifest,
        config_path,
        catalog_path,
        manifest_path,
        dataset_dir,
        findings,
    )
    raw_validation, oracle = validate_raw_predictions(
        config,
        assay_result,
        recipe,
        datasets,
        raw_dir,
        evaluation_entries,
        findings,
    )
    solver_validation = validate_solver_baselines(
        config,
        assay_result,
        datasets,
        oracle,
        findings,
    )
    control_validation = validate_control_summary(
        selection_result,
        assay_result,
        findings,
    )

    selection_commit = recipe.get("source_commit")
    evaluation_commit = assay_result.get("source_commit")
    for field in (
        "source_commit",
        "source_worktree_dirty_before_run",
        "producer_sha256",
        "config_sha256",
        "preregistration_sha256",
        "catalog_sha256",
        "manifest_sha256",
        "curve_validation_sha256",
        "dataset_validation_sha256",
        "selection_ledger_sha256",
        "metric_baseline",
        "dataset_records",
        "source_dependency_sha256",
        "runtime_versions",
    ):
        if selection_result.get(field) != recipe.get(field):
            findings.error(
                f"selection result and frozen recipe differ on {field}"
            )
    if recipe.get("source_worktree_dirty_before_run") is not False:
        findings.error("selection did not start from a clean worktree")
    if selection_result.get("source_worktree_dirty_before_run") is not False:
        findings.error("selection result records a dirty starting worktree")
    if assay_result.get("source_worktree_dirty_before_run") is not False:
        findings.error("evaluation did not start from a clean worktree")
    if not git_commit_exists(selection_commit):
        findings.error("selection source commit does not resolve")
    if not git_commit_exists(evaluation_commit):
        findings.error("evaluation source commit does not resolve")
    if git_commit_exists(selection_commit) and git_commit_exists(evaluation_commit):
        if not is_ancestor(selection_commit, evaluation_commit):
            findings.error("selection source commit is not an ancestor of evaluation")
        runner_blob = git_blob(
            str(selection_commit), ROOT / RUNNER_RELATIVE_PATH
        )
        if runner_blob is None:
            findings.error("run_assay.py is absent at selection source commit")
        elif hashlib.sha256(runner_blob).hexdigest() != recipe.get(
            "producer_sha256"
        ):
            findings.error("recipe producer hash differs from selection source")
        recorded_dependencies = recipe.get("source_dependency_sha256")
        if not isinstance(recorded_dependencies, dict):
            findings.error("recipe source dependency hashes are missing")
            recorded_dependencies = {}
        if set(recorded_dependencies) != set(SOURCE_DEPENDENCY_RELATIVE_PATHS):
            findings.error("recipe source dependency hash set is unexpected")
        for name, relative in SOURCE_DEPENDENCY_RELATIVE_PATHS.items():
            for label, commit in (
                ("selection", selection_commit),
                ("evaluation", evaluation_commit),
            ):
                blob = git_blob(str(commit), ROOT / relative)
                if blob is None:
                    findings.error(
                        f"{name} is absent at {label} source commit"
                    )
                elif hashlib.sha256(blob).hexdigest() != (
                    recorded_dependencies.get(name)
                ):
                    findings.error(
                        f"{name} differs from frozen dependency at "
                        f"{label} source commit"
                    )
        for path, label in (
            (preregistration_path, "preregistration"),
            (config_path, "configuration"),
            (catalog_path, "curve catalog"),
            (manifest_path, "dataset manifest"),
            (curve_validation_path, "curve validation"),
            (dataset_validation_path, "dataset validation"),
            (
                ROOT
                / "experiments/ml_structure_probe/p1_toy_scaling/"
                "validate_curves.py",
                "curve validator source",
            ),
            (
                ROOT
                / "experiments/ml_structure_probe/p1_toy_scaling/"
                "validate_dataset.py",
                "dataset validator source",
            ),
            (
                ROOT / "experiments/framework/ec_oracle.py",
                "framework EC oracle",
            ),
        ):
            require_committed_file(findings, selection_commit, path, label)
        require_committed_file(
            findings, evaluation_commit, recipe_path, "frozen recipe"
        )
        require_committed_file(
            findings,
            evaluation_commit,
            selection_ledger_path,
            "selection ledger",
        )
        require_committed_file(
            findings,
            evaluation_commit,
            selection_result_path,
            "selection result",
        )

    limitations = [
        (
            "Control decisions are rebound to their selection-ledger rows, "
            "but the producer does not retain raw control predictions for "
            "independent metric replay."
        ),
        (
            "Screen and confirmation scores are independently re-aggregated "
            "from the selection ledger, but their per-fit metrics cannot be "
            "recomputed because selection predictions are not retained."
        ),
        (
            "Solver-baseline candidate scalars and summary arithmetic are "
            "independently checked, but the BSGS and Pollard-rho searches "
            "themselves are not rerun."
        ),
        (
            "Raw ensemble probabilities are validated as decisive artifacts, "
            "but per-seed raw predictions are not retained, so their averaging "
            "cannot be reconstructed independently."
        ),
    ]
    return {
        "schema_version": 1,
        "experiment_id": experiment_id,
        "validation_role": (
            "independent metric, artifact, recipe, ledger, and EC recovery replay"
        ),
        "producer_modules_imported": False,
        "framework_oracle": "experiments.framework.ec_oracle",
        "validator_sha256": sha256_file(Path(__file__).resolve()),
        "framework_oracle_sha256": sha256_file(
            ROOT / "experiments/framework/ec_oracle.py"
        ),
        "validation_environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy_version,
        },
        "status": "pass" if findings.error_count == 0 else "fail",
        "error_count": findings.error_count,
        "errors": findings.errors,
        "errors_truncated": findings.error_count > len(findings.errors),
        "warnings": findings.warnings,
        "bindings": {
            "config_sha256": sha256_file(config_path),
            "preregistration_sha256": sha256_file(preregistration_path),
            "catalog_sha256": sha256_file(catalog_path),
            "manifest_sha256": sha256_file(manifest_path),
            "curve_validation_sha256": sha256_file(curve_validation_path),
            "dataset_validation_sha256": sha256_file(
                dataset_validation_path
            ),
            "selection_result_sha256": sha256_file(selection_result_path),
            "selection_ledger_sha256": sha256_file(selection_ledger_path),
            "recipe_sha256": recipe_sha,
            "evaluation_result_sha256": sha256_file(assay_result_path),
            "evaluation_ledger_sha256": sha256_file(evaluation_ledger_path),
        },
        "input_validation": input_validation,
        "selection": selection_validation,
        "evaluation_run_counts": evaluation_counts,
        "raw_prediction_validation": raw_validation,
        "solver_baseline_validation": solver_validation,
        "control_validation": control_validation,
        "oracle_recovery": {
            "candidate_submissions": oracle.submissions,
            "ec_scalar_multiplications": oracle.checks,
            "cached_replays": oracle.cache_hits,
            "valid_recovery_submissions": oracle.valid_recoveries,
            "rejected_candidate_submissions": oracle.rejected_candidates,
            "out_of_range_submissions": oracle.out_of_range,
            "curve_instances": len(oracle.curves),
        },
        "limitations": limitations,
        "wall_time_seconds": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--curve-validation", type=Path, required=True)
    parser.add_argument("--dataset-validation", type=Path, required=True)
    parser.add_argument("--dataset-dir", type=Path, required=True)
    parser.add_argument("--selection-result", type=Path, required=True)
    parser.add_argument("--selection-ledger", type=Path, required=True)
    parser.add_argument("--recipe", type=Path, required=True)
    parser.add_argument("--assay-result", type=Path, required=True)
    parser.add_argument("--evaluation-ledger", type=Path, required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = validate(
        config_path=args.config.resolve(),
        preregistration_path=args.preregistration.resolve(),
        catalog_path=args.catalog.resolve(),
        manifest_path=args.manifest.resolve(),
        curve_validation_path=args.curve_validation.resolve(),
        dataset_validation_path=args.dataset_validation.resolve(),
        dataset_dir=args.dataset_dir.resolve(),
        selection_result_path=args.selection_result.resolve(),
        selection_ledger_path=args.selection_ledger.resolve(),
        recipe_path=args.recipe.resolve(),
        assay_result_path=args.assay_result.resolve(),
        evaluation_ledger_path=args.evaluation_ledger.resolve(),
        raw_dir=args.raw_dir.resolve(),
    )
    args.output.resolve().parent.mkdir(parents=True, exist_ok=True)
    args.output.resolve().write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"P1E result validation {result['status']}: "
        f"{result['oracle_recovery']['ec_scalar_multiplications']} "
        "EC scalar multiplications, "
        f"{result['error_count']} errors"
    )
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
