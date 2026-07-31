#!/usr/bin/env python3
"""Fail-closed producer for HYP-M16-FIXED-TARGET-YIELD-001.

The producer uses exact prime-field arithmetic and deterministic SHA-256
counter streams.  It never receives or records a target scalar.  The only CLI
operation available before a separately merged authorization is
``--check-readiness``.  After that authorization, ``--check-authorization``
replays the complete pre-execution gate without writing output or sampling a
primary trial; ``--execute`` checks the same canonical singleton before
creating output or sampling one primary trial.

This module is deliberately self-contained.  The independent validator must
not import it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import resource
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, TextIO


HYPOTHESIS_ID = "HYP-M16-FIXED-TARGET-YIELD-001"
TASK_ID = "TASK-026"
ROUTE_ID = "R-PETIT-COMPOSED-MAPS"
CELL_ID = "CELL-M-PKC-SMOOTH-M16"
SCHEMA_VERSION = "keyai-m16-fixed-target-producer-v1"
RAW_SCHEMA_VERSION = "keyai-m16-fixed-target-raw-v1"
SUMMARY_SCHEMA_VERSION = "keyai-m16-fixed-target-summary-v1"
PRNG_PREFIX = b"KEYAI-HYP-M16-FIXED-TARGET-YIELD-001/sha256-counter-v1\x00"
TARGET_STATEMENT = "target-frozen-before-leaf-stream-v1"
BASE_STATEMENT = "ordered-factor-base-v1"
AUTHORIZATION_KEY = "bounded_experiment_authorization"

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
DEFAULT_CONFIG = HERE / "experiment_config.json"
DEFAULT_CURVE_TABLE = HERE / "curve_table.json"
DEFAULT_PREREGISTRATION = HERE / "PREREGISTRATION.md"
DEFAULT_AUTHORIZATION_SUBSTRATE = REPO_ROOT / "repo/ECDLP_DECISION_SUBSTRATE.json"
DEFAULT_VALIDATOR = HERE / "validate.py"

Point = tuple[int, int] | None


class ReadinessError(RuntimeError):
    """A frozen readiness binding is absent or inconsistent."""


class AuthorizationError(RuntimeError):
    """The canonical execution authorization is absent or inconsistent."""


def canonical_bytes(value: Any) -> bytes:
    """Canonical JSON used by every producer-side commitment."""
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise ReadinessError(f"cannot load canonical JSON {path}: {error}") from error


def point_json(point: Point) -> dict[str, int] | None:
    if point is None:
        return None
    return {"x": point[0], "y": point[1]}


def parse_point(value: object, label: str) -> Point:
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != {"x", "y"}:
        raise ReadinessError(f"{label} must have exactly x and y")
    x = value["x"]
    y = value["y"]
    if not isinstance(x, int) or isinstance(x, bool):
        raise ReadinessError(f"{label}.x must be an integer")
    if not isinstance(y, int) or isinstance(y, bool):
        raise ReadinessError(f"{label}.y must be an integer")
    return x, y


def is_prime(value: int) -> bool:
    """Deterministic primality check for the frozen at-most-25-bit inputs."""
    if value < 2:
        return False
    for small in (2, 3, 5):
        if value == small:
            return True
        if value % small == 0:
            return False
    divisor = 7
    step = 4
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += step
        step = 6 - step
    return True


@dataclass
class OperationCounts:
    curve_additions: int = 0
    curve_doublings: int = 0
    identity_shortcuts: int = 0
    field_inversions: int = 0
    scalar_multiplication_bits: int = 0

    def snapshot(self) -> dict[str, int]:
        return asdict(self)

    def delta(self, earlier: dict[str, int]) -> dict[str, int]:
        now = self.snapshot()
        return {key: now[key] - earlier[key] for key in now}

    def absorb(self, other: "OperationCounts") -> None:
        for key, value in asdict(other).items():
            setattr(self, key, getattr(self, key) + value)

    def absorb_mapping(self, other: dict[str, int]) -> None:
        expected = set(asdict(self))
        if set(other) != expected:
            raise ValueError("operation-count key mismatch")
        for key, value in other.items():
            if not isinstance(value, int) or value < 0:
                raise ValueError("operation counts must be nonnegative integers")
            setattr(self, key, getattr(self, key) + value)


class Curve:
    """Exact short-Weierstrass arithmetic with operation instrumentation."""

    def __init__(
        self,
        p: int,
        a: int,
        b: int,
        counter: OperationCounts | None = None,
    ) -> None:
        if not is_prime(p) or p <= 3:
            raise ReadinessError("curve modulus must be prime and greater than 3")
        if (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p == 0:
            raise ReadinessError("singular curve")
        self.p = p
        self.a = a % p
        self.b = b % p
        self.counter = counter if counter is not None else OperationCounts()

    def is_on_curve(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return (
            0 <= x < self.p
            and 0 <= y < self.p
            and (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0
        )

    def negate(self, point: Point) -> Point:
        if point is None:
            return None
        return point[0], (-point[1]) % self.p

    def add(self, left: Point, right: Point) -> Point:
        if not self.is_on_curve(left) or not self.is_on_curve(right):
            raise ValueError("point_add received an off-curve point")
        if left is None:
            self.counter.identity_shortcuts += 1
            return right
        if right is None:
            self.counter.identity_shortcuts += 1
            return left
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and (y1 + y2) % self.p == 0:
            self.counter.curve_additions += 1
            return None
        if left == right:
            self.counter.curve_doublings += 1
            denominator = (2 * y1) % self.p
            if denominator == 0:
                return None
            numerator = (3 * x1 * x1 + self.a) % self.p
        else:
            self.counter.curve_additions += 1
            denominator = (x2 - x1) % self.p
            if denominator == 0:
                return None
            numerator = (y2 - y1) % self.p
        self.counter.field_inversions += 1
        slope = numerator * pow(denominator, -1, self.p) % self.p
        x3 = (slope * slope - x1 - x2) % self.p
        y3 = (slope * (x1 - x3) - y1) % self.p
        result = (x3, y3)
        if not self.is_on_curve(result):
            raise AssertionError("exact arithmetic produced an off-curve point")
        return result

    def subtract(self, left: Point, right: Point) -> Point:
        return self.add(left, self.negate(right))

    def scalar_mul(self, scalar: int, point: Point) -> Point:
        if not isinstance(scalar, int) or isinstance(scalar, bool):
            raise TypeError("scalar must be an integer")
        if not self.is_on_curve(point):
            raise ValueError("scalar_mul received an off-curve point")
        if scalar < 0:
            return self.scalar_mul(-scalar, self.negate(point))
        self.counter.scalar_multiplication_bits += scalar.bit_length()
        result: Point = None
        addend = point
        remaining = scalar
        while remaining:
            if remaining & 1:
                result = self.add(result, addend)
            remaining >>= 1
            if remaining:
                addend = self.add(addend, addend)
        return result

    def sum(self, points: Iterable[Point]) -> Point:
        result: Point = None
        for point in points:
            result = self.add(result, point)
        return result


class CounterPRNG:
    """SHA-256 counter PRNG with unbiased rejection sampling."""

    def __init__(self, domain: str) -> None:
        domain_bytes = domain.encode("utf-8")
        self._material = (
            PRNG_PREFIX
            + len(domain_bytes).to_bytes(4, "big")
            + domain_bytes
        )
        self.counter = 0
        self.rejected_blocks = 0

    def block(self) -> bytes:
        if self.counter >= 1 << 128:
            raise OverflowError("SHA-256 counter exhausted")
        value = hashlib.sha256(
            self._material + self.counter.to_bytes(16, "big")
        ).digest()
        self.counter += 1
        return value

    def randbelow(self, bound: int) -> int:
        if not isinstance(bound, int) or isinstance(bound, bool) or bound <= 0:
            raise ValueError("bound must be a positive integer")
        modulus = 1 << 256
        limit = modulus - modulus % bound
        while True:
            candidate = int.from_bytes(self.block(), "big")
            if candidate < limit:
                return candidate % bound
            self.rejected_blocks += 1


def stream_domain(
    curve_id: str,
    arm: str,
    seed: int,
    role: str,
) -> str:
    return f"{HYPOTHESIS_ID}/{curve_id}/{arm}/{seed}/{role}"


def cell_id(curve_id: str, arm: str, seed: int) -> str:
    return f"{curve_id}--{arm}--S{seed}"


@dataclass
class BaseBuild:
    points: list[Point]
    commitment: str
    selection_counts: dict[str, int]
    prng_blocks: int
    prng_rejected_blocks: int
    operation_counts: dict[str, int]


def base_commitment(
    curve_id: str,
    arm: str,
    seed: int,
    points: list[Point],
) -> str:
    body = {
        "arm": arm,
        "cell_id": cell_id(curve_id, arm, seed),
        "curve_id": curve_id,
        "points": [point_json(point) for point in points],
        "seed": seed,
        "statement": BASE_STATEMENT,
    }
    return sha256_bytes(canonical_bytes(body))


def build_factor_base(
    curve_row: dict[str, Any],
    arm: str,
    seed: int,
    size: int,
) -> BaseBuild:
    """Reconstruct one ordered base from its public deterministic stream."""
    curve_id_value = curve_row["curve_id"]
    p = curve_row["p"]
    n = curve_row["n"]
    beta = curve_row["beta"]
    generator = parse_point(curve_row["generator"], "generator")
    if generator is None:
        raise ReadinessError("generator cannot be the identity")
    counter = OperationCounts()
    curve = Curve(p, 0, 7, counter)
    prng = CounterPRNG(stream_domain(curve_id_value, arm, seed, "base"))
    points: list[Point] = []
    used_x: set[int] = set()
    counts = {
        "draws": 0,
        "rejected_zero_scalar": 0,
        "rejected_x_collision": 0,
        "rejected_orbit_collision": 0,
        "accepted_plain_orbit_relation": 0,
    }

    if arm == "GLV_ORBIT_CLOSED":
        if size % 3 != 0:
            raise ReadinessError("orbit-closed base size must be divisible by 3")
        while len(points) < size:
            counts["draws"] += 1
            scalar = prng.randbelow(n - 1) + 1
            point = curve.scalar_mul(scalar, generator)
            if point is None:
                raise AssertionError("nonzero prime-subgroup scalar gave identity")
            orbit = [
                point,
                (point[0] * beta % p, point[1]),
                (point[0] * beta * beta % p, point[1]),
            ]
            orbit_x = [item[0] for item in orbit]
            if len(set(orbit_x)) != 3:
                counts["rejected_orbit_collision"] += 1
                continue
            if any(x in used_x for x in orbit_x):
                counts["rejected_x_collision"] += 1
                continue
            if any(not curve.is_on_curve(item) for item in orbit):
                raise AssertionError("GLV orbit left E_7")
            points.extend(orbit)
            used_x.update(orbit_x)
    elif arm == "PLAIN_MATCHED":
        while len(points) < size:
            counts["draws"] += 1
            scalar = prng.randbelow(n - 1) + 1
            point = curve.scalar_mul(scalar, generator)
            if point is None:
                raise AssertionError("nonzero prime-subgroup scalar gave identity")
            x = point[0]
            if x in used_x:
                counts["rejected_x_collision"] += 1
                continue
            if (
                x * beta % p in used_x
                or x * beta * beta % p in used_x
            ):
                counts["accepted_plain_orbit_relation"] += 1
            points.append(point)
            used_x.add(x)
    else:
        raise ReadinessError(f"unknown factor-base arm: {arm}")

    if len(points) != size or len(used_x) != size:
        raise AssertionError("factor-base cardinality invariant failed")
    return BaseBuild(
        points=points,
        commitment=base_commitment(curve_id_value, arm, seed, points),
        selection_counts=counts,
        prng_blocks=prng.counter,
        prng_rejected_blocks=prng.rejected_blocks,
        operation_counts=counter.snapshot(),
    )


def target_commitment(target: dict[str, Any]) -> str:
    body = {
        "base_commitment": target["base_commitment"],
        "cell_id": target["cell_id"],
        "point": target["point"],
        "statement": target["statement"],
    }
    return sha256_bytes(canonical_bytes(body))


def verify_curve_table(table: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if not isinstance(table, dict):
        raise ReadinessError("curve table must be a JSON object")
    if table.get("schema_version") != "keyai-m16-fixed-target-curve-table-v1":
        raise ReadinessError("unexpected curve-table schema")
    if table.get("hypothesis_id") != HYPOTHESIS_ID:
        raise ReadinessError("curve table binds the wrong hypothesis")
    family = table.get("curve_family")
    if family != {
        "a": 0,
        "b": 7,
        "equation": "y^2 = x^3 + 7",
        "field": "prime",
    }:
        raise ReadinessError("curve family is not the exact frozen E_7 family")
    rows = table.get("curves")
    if not isinstance(rows, list) or len(rows) != 3:
        raise ReadinessError("curve table must contain exactly three rows")
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        curve_id_value = row.get("curve_id")
        if not isinstance(curve_id_value, str) or curve_id_value in result:
            raise ReadinessError("curve ids must be unique strings")
        p = row.get("p")
        n = row.get("n")
        order = row.get("declared_order")
        cofactor = row.get("cofactor")
        if not all(
            isinstance(value, int) and not isinstance(value, bool)
            for value in (p, n, order, cofactor)
        ):
            raise ReadinessError(f"{curve_id_value}: noninteger order data")
        if not is_prime(p) or not is_prime(n):
            raise ReadinessError(f"{curve_id_value}: p or n is not prime")
        if row.get("field_bits") != p.bit_length():
            raise ReadinessError(f"{curve_id_value}: wrong field_bits")
        if row.get("m") != (n - 1).bit_length():
            raise ReadinessError(f"{curve_id_value}: wrong m=ceil(log2 n)")
        if order != cofactor * n:
            raise ReadinessError(f"{curve_id_value}: cofactor binding failed")
        deviation = order - (p + 1)
        if deviation * deviation > 4 * p:
            raise ReadinessError(f"{curve_id_value}: order is outside Hasse")
        if n * n <= 16 * p:
            raise ReadinessError(
                f"{curve_id_value}: subgroup does not isolate a Hasse multiple"
            )
        cert = row.get("certificate")
        expected_cert = {
            "hasse_deviation": deviation,
            "hasse_deviation_squared": deviation * deviation,
            "four_p": 4 * p,
            "n_squared": n * n,
            "sixteen_p": 16 * p,
        }
        if cert != expected_cert:
            raise ReadinessError(f"{curve_id_value}: stale Hasse certificate")
        counter = OperationCounts()
        curve = Curve(p, 0, 7, counter)
        generator = parse_point(row.get("generator"), "generator")
        if generator is None or not curve.is_on_curve(generator):
            raise ReadinessError(f"{curve_id_value}: invalid generator")
        if curve.scalar_mul(n, generator) is not None:
            raise ReadinessError(f"{curve_id_value}: [n]G is not the identity")
        beta = row.get("beta")
        lam = row.get("lambda")
        if not isinstance(beta, int) or not isinstance(lam, int):
            raise ReadinessError(f"{curve_id_value}: invalid beta/lambda")
        if pow(beta, 3, p) != 1 or beta % p == 1:
            raise ReadinessError(f"{curve_id_value}: beta is not order three")
        if (lam * lam + lam + 1) % n != 0:
            raise ReadinessError(f"{curve_id_value}: lambda polynomial failed")
        phi_g = (generator[0] * beta % p, generator[1])
        if not curve.is_on_curve(phi_g):
            raise ReadinessError(f"{curve_id_value}: phi(G) is off curve")
        if curve.scalar_mul(lam, generator) != phi_g:
            raise ReadinessError(f"{curve_id_value}: GLV eigenvalue failed")
        result[curve_id_value] = row
    return result


def verify_config(
    config: dict[str, Any],
    curve_rows: dict[str, dict[str, Any]],
    config_path: Path,
    curve_table_path: Path,
) -> list[dict[str, Any]]:
    if not isinstance(config, dict):
        raise ReadinessError("experiment config must be a JSON object")
    if config.get("schema_version") != "keyai-m16-fixed-target-config-v1":
        raise ReadinessError("unexpected experiment-config schema")
    exact_ids = {
        "hypothesis_id": HYPOTHESIS_ID,
        "task_id": TASK_ID,
        "route_id": ROUTE_ID,
        "cell_id": CELL_ID,
    }
    for key, expected in exact_ids.items():
        if config.get(key) != expected:
            raise ReadinessError(f"config {key} binding failed")
    if config.get("preregistration_sha256") != sha256_file(
        DEFAULT_PREREGISTRATION
    ):
        raise ReadinessError("preregistration hash mismatch")
    if config.get("curve_table_sha256") != sha256_file(curve_table_path):
        raise ReadinessError("curve-table hash mismatch")
    if config.get("factor_base_size") != 384:
        raise ReadinessError("factor-base size is not 384")
    if config.get("relation_arity") != 16:
        raise ReadinessError("relation arity is not 16")
    if config.get("sampled_leaves_per_trial") != 15:
        raise ReadinessError("sampled-leaf count is not 15")
    if config.get("permutation_controls") != 16:
        raise ReadinessError("permutation-control count is not 16")
    if config.get("curve_ids") != list(curve_rows):
        raise ReadinessError("curve ordering is not frozen")
    arms = config.get("arms")
    if arms != ["GLV_ORBIT_CLOSED", "PLAIN_MATCHED"]:
        raise ReadinessError("factor-base arms are not frozen")
    seeds = config.get("seeds")
    if (
        not isinstance(seeds, list)
        or len(seeds) != 5
        or len(set(seeds)) != 5
        or any(not isinstance(seed, int) for seed in seeds)
    ):
        raise ReadinessError("five unique integer seeds are required")
    prng = config.get("prng")
    expected_prng = {
        "algorithm": "sha256-counter-rejection-v1",
        "prefix_hex": PRNG_PREFIX.hex(),
        "counter_bytes": 16,
        "counter_endian": "big",
        "domain_length_bytes": 4,
        "domain_length_endian": "big",
        "digest_integer_endian": "big",
        "randbelow": "reject x >= 2^256-(2^256 mod bound), return x mod bound",
        "domain_template": (
            "HYP-M16-FIXED-TARGET-YIELD-001/{curve_id}/{arm}/"
            "{seed}/{role}"
        ),
    }
    if prng != expected_prng:
        raise ReadinessError("PRNG contract mismatch")
    if config.get("target_generation_contract") != {
        "arm_domain_literal": "PAIRED_TARGET",
        "role": "target",
        "scalar_draw": "randbelow(n-1)+1",
        "scalar_persisted": False,
        "same_public_point_in_both_arms": True,
        "runtime_sampler_inputs": [
            "curve",
            "ordered factor base",
            "public target point",
            "leaf stream",
        ],
        "commitment": (
            "SHA256(canonical compact sorted-key JSON plus LF of "
            "base_commitment, cell_id, point, and statement)"
        ),
    }:
        raise ReadinessError("paired-target generation contract mismatch")
    trial_caps = config.get("trials_per_seed")
    if trial_caps != {
        "E7-P262153-N262567": 10000,
        "E7-P1048783-N1050337": 40000,
        "E7-P16777711-N5591281": 250000,
    }:
        raise ReadinessError("trial caps differ from preregistration")
    expected_total = sum(trial_caps[curve_id_value] for curve_id_value in curve_rows)
    expected_total *= len(arms) * len(seeds)
    if expected_total != 3_000_000:
        raise AssertionError("frozen grid no longer totals three million trials")
    budget = config.get("resource_budget")
    if budget != {
        "max_primary_trials": 3000000,
        "max_cpu_hours": 4,
        "max_peak_rss_gib": 4,
        "max_wall_hours": 24,
    }:
        raise ReadinessError("resource budget differs from preregistration")
    if config.get("decision_thresholds") != {
        "minimum_accepted_per_curve_arm": 100,
        "promotion_orbit_theta_wilson95_lower": 0.9,
        "promotion_orbit_maximum_unexplained_m21_to_m23_decline": 0.05,
        "kill_orbit_theta_wilson95_upper": 0.8,
        "known_local_plain_theta_wilson95_lower": 0.9,
        "known_local_maximum_absolute_arm_delta": 0.05,
        "known_local_requires_interval_overlap": True,
        "h_new": {
            "minimum_qualifying_sizes": 2,
            "primary_pooled_orbit_minus_plain_minimum": 0.1,
            "primary_intervals_nonoverlapping": True,
            "minimum_positive_paired_seeds_per_size": 4,
            "shuffled_minimum_accepted_per_arm_size": 100,
            "shuffled_pooled_orbit_minus_plain_minimum": 0.05,
            "permutation_mean_orbit_minus_plain_minimum": 0.05,
            "permutation_minimum_positive_paired_seeds_per_size": 4,
            "random_label_rate_interval": [0.35, 0.65],
            "random_label_maximum_absolute_arm_delta": 0.15,
            "failed_control_blocks_h_new_only": True,
        },
    }:
        raise ReadinessError("decision thresholds differ from preregistration")

    base_manifest = config.get("base_manifest")
    if not isinstance(base_manifest, list) or len(base_manifest) != 30:
        raise ReadinessError("base manifest must contain exactly 30 cells")
    base_by_cell: dict[str, dict[str, Any]] = {}
    for entry in base_manifest:
        entry_cell = entry.get("cell_id")
        if not isinstance(entry_cell, str) or entry_cell in base_by_cell:
            raise ReadinessError("duplicate or invalid base cell id")
        curve_id_value = entry.get("curve_id")
        arm = entry.get("arm")
        seed = entry.get("seed")
        if (
            curve_id_value not in curve_rows
            or arm not in arms
            or seed not in seeds
            or entry_cell != cell_id(curve_id_value, arm, seed)
        ):
            raise ReadinessError(f"{entry_cell}: invalid base identity")
        if entry.get("frozen_sequence") != 1:
            raise ReadinessError(f"{entry_cell}: base chronology is not first")
        expected_hash = entry.get("ordered_base_sha256")
        if not isinstance(expected_hash, str) or len(expected_hash) != 64:
            raise ReadinessError(f"{entry_cell}: invalid base commitment")
        base_by_cell[entry_cell] = entry

    targets = config.get("targets")
    if not isinstance(targets, list) or len(targets) != 30:
        raise ReadinessError("target manifest must contain exactly 30 cells")
    target_by_cell: dict[str, dict[str, Any]] = {}
    for target in targets:
        entry_cell = target.get("cell_id")
        if not isinstance(entry_cell, str) or entry_cell in target_by_cell:
            raise ReadinessError("duplicate or invalid target cell id")
        if entry_cell not in base_by_cell:
            raise ReadinessError(f"{entry_cell}: target has no frozen base")
        base_entry = base_by_cell[entry_cell]
        for key in ("curve_id", "arm", "seed"):
            if target.get(key) != base_entry.get(key):
                raise ReadinessError(f"{entry_cell}: target identity mismatch")
        if target.get("frozen_sequence") != 2:
            raise ReadinessError(f"{entry_cell}: target chronology is not second")
        if target.get("base_commitment") != base_entry.get(
            "ordered_base_sha256"
        ):
            raise ReadinessError(
                f"{entry_cell}: target does not bind its frozen base"
            )
        if target.get("statement") != TARGET_STATEMENT:
            raise ReadinessError(f"{entry_cell}: target statement mismatch")
        if target.get("commitment") != target_commitment(target):
            raise ReadinessError(f"{entry_cell}: target commitment mismatch")
        point = parse_point(target.get("point"), f"{entry_cell}.target")
        if point is None:
            raise ReadinessError(f"{entry_cell}: target cannot be identity")
        row = curve_rows[target["curve_id"]]
        curve = Curve(row["p"], 0, 7)
        if not curve.is_on_curve(point):
            raise ReadinessError(f"{entry_cell}: target is off curve")
        if curve.scalar_mul(row["n"], point) is not None:
            raise ReadinessError(f"{entry_cell}: target is outside <G>")
        target_stream = CounterPRNG(
            stream_domain(
                target["curve_id"],
                "PAIRED_TARGET",
                target["seed"],
                "target",
            )
        )
        transient_scalar = target_stream.randbelow(row["n"] - 1) + 1
        generator = parse_point(row["generator"], "generator")
        if generator is None:
            raise AssertionError("verified generator became identity")
        if curve.scalar_mul(transient_scalar, generator) != point:
            raise ReadinessError(
                f"{entry_cell}: target does not match its frozen target stream"
            )
        shuffled = target.get("shuffled_target_cell_id")
        if not isinstance(shuffled, str):
            raise ReadinessError(f"{entry_cell}: missing shuffled-target binding")
        target_by_cell[entry_cell] = target
    for target in targets:
        shuffled = target["shuffled_target_cell_id"]
        if shuffled not in target_by_cell:
            raise ReadinessError("shuffled target references an unknown cell")
        peer = target_by_cell[shuffled]
        if (
            peer["curve_id"] != target["curve_id"]
            or peer["arm"] != target["arm"]
            or peer["seed"] == target["seed"]
        ):
            raise ReadinessError("shuffled target is not a distinct matched peer")
        seed_index = seeds.index(target["seed"])
        expected_seed = seeds[(seed_index + 1) % len(seeds)]
        expected_shuffled = cell_id(
            target["curve_id"], target["arm"], expected_seed
        )
        if shuffled != expected_shuffled:
            raise ReadinessError(
                "shuffled target mapping is not the frozen cyclic successor"
            )
        paired_cell = cell_id(
            target["curve_id"],
            (
                "PLAIN_MATCHED"
                if target["arm"] == "GLV_ORBIT_CLOSED"
                else "GLV_ORBIT_CLOSED"
            ),
            target["seed"],
        )
        if target_by_cell[paired_cell]["point"] != target["point"]:
            raise ReadinessError(
                "matched arms do not share their frozen paired target"
            )
    if set(base_by_cell) != set(target_by_cell):
        raise ReadinessError("base and target manifests cover different cells")

    auth_contract = config.get("authorization_contract")
    if auth_contract != {
        "path": "repo/ECDLP_DECISION_SUBSTRATE.json",
        "singleton_key": AUTHORIZATION_KEY,
        "required_status": "approved",
        "promotion_authorized": False,
    }:
        raise ReadinessError("authorization contract is not fail-closed")
    output = config.get("output_contract")
    if output != {
        "manifest": "run_manifest.json",
        "raw_jsonl": "raw/transcript.jsonl",
        "summary": "summary.json",
        "validated_artifact": "artifact.json",
        "validated_sidecar": "artifact.sha256",
        "canonical_json": (
            "UTF-8, sorted keys, compact separators, one trailing LF"
        ),
        "event_order": [
            "run_header",
            "base",
            "target",
            "constructed_control",
            "accepted",
            "shuffled_accepted",
            "cell_summary",
            "run_summary",
        ],
    }:
        raise ReadinessError("output contract mismatch")
    return targets


def reconstruct_and_verify_bases(
    config: dict[str, Any],
    curve_rows: dict[str, dict[str, Any]],
) -> dict[str, BaseBuild]:
    result: dict[str, BaseBuild] = {}
    size = config["factor_base_size"]
    for entry in config["base_manifest"]:
        built = build_factor_base(
            curve_rows[entry["curve_id"]],
            entry["arm"],
            entry["seed"],
            size,
        )
        if built.commitment != entry["ordered_base_sha256"]:
            raise ReadinessError(
                f"{entry['cell_id']}: ordered factor-base hash mismatch"
            )
        result[entry["cell_id"]] = built
    return result


def no_outcomes_present(config: dict[str, Any]) -> None:
    forbidden = [
        HERE / "artifact.json",
        HERE / "artifact.sha256",
        HERE / "RESULTS.md",
        HERE / config["output_contract"]["manifest"],
        HERE / config["output_contract"]["summary"],
        HERE / config["output_contract"]["raw_jsonl"],
    ]
    existing = [str(path.relative_to(HERE)) for path in forbidden if path.exists()]
    if existing:
        raise ReadinessError(
            "readiness branch contains forbidden outcome files: "
            + ", ".join(existing)
        )


def authorization_state(substrate_path: Path) -> str:
    substrate = load_json(substrate_path)
    if not isinstance(substrate, dict):
        raise ReadinessError("authorization substrate must be a JSON object")
    authorization = substrate.get(AUTHORIZATION_KEY)
    if authorization is None:
        return "absent"
    if not isinstance(authorization, dict):
        raise ReadinessError("authorization singleton is not an object")
    status = authorization.get("status")
    if not isinstance(status, str):
        raise ReadinessError("authorization singleton has no status")
    return status


def check_readiness(
    config_path: Path = DEFAULT_CONFIG,
    curve_table_path: Path = DEFAULT_CURVE_TABLE,
) -> dict[str, Any]:
    table = load_json(curve_table_path)
    curve_rows = verify_curve_table(table)
    config = load_json(config_path)
    targets = verify_config(config, curve_rows, config_path, curve_table_path)
    bases = reconstruct_and_verify_bases(config, curve_rows)
    no_outcomes_present(config)
    auth_state = authorization_state(DEFAULT_AUTHORIZATION_SUBSTRATE)
    if auth_state == "approved":
        raise ReadinessError(
            "readiness-only check expects authorization absent or closed"
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "curve_count": len(curve_rows),
        "cell_count": len(targets),
        "factor_base_points_checked": sum(
            len(build.points) for build in bases.values()
        ),
        "authorization_state": auth_state,
        "outcomes_present": False,
    }


def check_authorization(
    config_path: Path = DEFAULT_CONFIG,
    curve_table_path: Path = DEFAULT_CURVE_TABLE,
) -> dict[str, Any]:
    """Replay the exact approved gate without creating scientific outcomes."""

    gate_time = datetime.now(timezone.utc)
    (
        config,
        curve_rows,
        targets,
        bases,
        authorization,
    ) = authorized_preflight(
        config_path,
        curve_table_path,
        authorization_not_after=gate_time,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "curve_count": len(curve_rows),
        "cell_count": len(targets),
        "factor_base_points_checked": sum(
            len(build.points) for build in bases.values()
        ),
        "authorization_state": authorization["status"],
        "authorization_id": authorization["authorization_id"],
        "source_commit": authorization["source_commit"],
        "outcomes_present": False,
    }


def authorized_preflight(
    config_path: Path,
    curve_table_path: Path,
    *,
    authorization_not_after: datetime,
) -> tuple[
    dict[str, Any],
    dict[str, dict[str, Any]],
    list[dict[str, Any]],
    dict[str, BaseBuild],
    dict[str, Any],
]:
    """Complete every immutable gate before execution may write one byte."""

    table = load_json(curve_table_path)
    curve_rows = verify_curve_table(table)
    config = load_json(config_path)
    targets = verify_config(config, curve_rows, config_path, curve_table_path)
    bases = reconstruct_and_verify_bases(config, curve_rows)
    no_outcomes_present(config)
    authorization = require_execution_authorization(
        config,
        config_path,
        curve_table_path,
        authorization_not_after=authorization_not_after,
    )
    return config, curve_rows, targets, bases, authorization


def signed_zero_exists(curve: Curve, points: list[Point]) -> bool:
    states: set[Point] = {None}
    for point in points:
        if point is None:
            raise ValueError("signed-zero input contains the identity")
        next_states: set[Point] = set()
        negative = curve.negate(point)
        for state in states:
            next_states.add(curve.add(state, point))
            next_states.add(curve.add(state, negative))
        states = next_states
    return None in states


def task025_labels(
    curve: Curve,
    coordinates: list[Point],
    target: Point,
) -> dict[str, Any]:
    if len(coordinates) != 16 or target is None:
        raise ValueError("TASK-025 labels require 16 affine points and a target")
    if any(point is None for point in coordinates):
        raise ValueError("coordinate tuple contains the identity")
    prefix_nonzero = [
        not signed_zero_exists(curve, coordinates[0 : j + 3])
        for j in range(6)
    ]
    suffix_nonzero = [
        not signed_zero_exists(
            curve,
            [target] + coordinates[14 - j : 16],
        )
        for j in range(6)
    ]
    base_endpoint = coordinates[0][0] != coordinates[1][0]
    final_endpoint = coordinates[15][0] != target[0]
    balanced_regular = all(prefix_nonzero) and all(suffix_nonzero)
    return {
        "base_endpoint_nonzero": base_endpoint,
        "final_endpoint_nonzero": final_endpoint,
        "prefix_nonzero": prefix_nonzero,
        "suffix_nonzero": suffix_nonzero,
        "balanced_regular": balanced_regular,
        "affine_regular": (
            base_endpoint and final_endpoint and balanced_regular
        ),
    }


def fisher_yates_permutation(size: int, prng: CounterPRNG) -> list[int]:
    permutation = list(range(size))
    for index in range(size - 1, 0, -1):
        swap = prng.randbelow(index + 1)
        permutation[index], permutation[swap] = (
            permutation[swap],
            permutation[index],
        )
    return permutation


def permutation_controls(
    curve: Curve,
    coordinates: list[Point],
    target: Point,
    curve_id_value: str,
    arm: str,
    seed: int,
    trial_index: int,
    count: int,
) -> list[dict[str, Any]]:
    controls: list[dict[str, Any]] = []
    for control_index in range(count):
        role = f"permutation/{trial_index}/{control_index}"
        prng = CounterPRNG(
            stream_domain(curve_id_value, arm, seed, role)
        )
        permutation = fisher_yates_permutation(len(coordinates), prng)
        permuted = [coordinates[index] for index in permutation]
        controls.append(
            {
                "control_index": control_index,
                "permutation": permutation,
                "labels": task025_labels(curve, permuted, target),
            }
        )
    return controls


@dataclass
class TrialResult:
    accepted: bool
    rejection_reason: str | None
    indices: list[int]
    signs: list[int]
    coordinates: list[Point]
    labels: dict[str, Any] | None
    repeated_index_count: int
    repeated_coordinate_count: int
    target_coordinate_collision_count: int
    operation_counts: dict[str, int]
    partial_sum: Point


def sample_primary_trial(
    curve: Curve,
    base: list[Point],
    base_x_to_index: dict[int, int],
    target: Point,
    leaf_stream: CounterPRNG,
) -> TrialResult:
    """Sample one exact trial; no target scalar exists in this API."""
    if target is None:
        raise ValueError("primary target cannot be the identity")
    before = curve.counter.snapshot()
    indices = [leaf_stream.randbelow(len(base)) for _ in range(15)]
    signs = [
        1 if leaf_stream.randbelow(2) == 1 else -1
        for _ in range(15)
    ]
    unsigned_points = [base[index] for index in indices]
    signed_points = [
        point if sign == 1 else curve.negate(point)
        for point, sign in zip(unsigned_points, signs, strict=True)
    ]
    partial_sum = curve.sum(signed_points)
    residual = curve.subtract(target, partial_sum)
    repeated_index_count = 15 - len(set(indices))
    repeated_coordinate_count = 15 - len(
        {point[0] for point in unsigned_points}
    )
    target_coordinate_collision_count = sum(
        point[0] == target[0] for point in unsigned_points
    )
    if residual is None:
        return TrialResult(
            accepted=False,
            rejection_reason="residual_identity",
            indices=indices,
            signs=signs,
            coordinates=[],
            labels=None,
            repeated_index_count=repeated_index_count,
            repeated_coordinate_count=repeated_coordinate_count,
            target_coordinate_collision_count=target_coordinate_collision_count,
            operation_counts=curve.counter.delta(before),
            partial_sum=partial_sum,
        )
    final_index = base_x_to_index.get(residual[0])
    if final_index is None:
        return TrialResult(
            accepted=False,
            rejection_reason="residual_not_in_base",
            indices=indices,
            signs=signs,
            coordinates=[],
            labels=None,
            repeated_index_count=repeated_index_count,
            repeated_coordinate_count=repeated_coordinate_count,
            target_coordinate_collision_count=target_coordinate_collision_count,
            operation_counts=curve.counter.delta(before),
            partial_sum=partial_sum,
        )
    final_point = base[final_index]
    if residual == final_point:
        final_sign = 1
    elif residual == curve.negate(final_point):
        final_sign = -1
    else:
        raise AssertionError("x-coordinate match did not identify either sign")
    all_indices = indices + [final_index]
    all_signs = signs + [final_sign]
    coordinates = unsigned_points + [final_point]
    replay = curve.sum(
        point if sign == 1 else curve.negate(point)
        for point, sign in zip(coordinates, all_signs, strict=True)
    )
    if replay != target:
        raise AssertionError("accepted relation failed exact replay")
    labels = task025_labels(curve, coordinates, target)
    return TrialResult(
        accepted=True,
        rejection_reason=None,
        indices=all_indices,
        signs=all_signs,
        coordinates=coordinates,
        labels=labels,
        repeated_index_count=16 - len(set(all_indices)),
        repeated_coordinate_count=16
        - len({point[0] for point in coordinates}),
        target_coordinate_collision_count=sum(
            point[0] == target[0] for point in coordinates
        ),
        operation_counts=curve.counter.delta(before),
        partial_sum=partial_sum,
    )


def constructed_target_control(
    curve: Curve,
    base: list[Point],
    curve_id_value: str,
    arm: str,
    seed: int,
) -> dict[str, Any]:
    """Leaves-first arithmetic control, excluded from every primary estimate."""
    for attempt in range(1 << 32):
        role = f"constructed-control/{attempt}"
        prng = CounterPRNG(
            stream_domain(curve_id_value, arm, seed, role)
        )
        indices = [prng.randbelow(len(base)) for _ in range(16)]
        signs = [1 if prng.randbelow(2) == 1 else -1 for _ in range(16)]
        coordinates = [base[index] for index in indices]
        signed = [
            point if sign == 1 else curve.negate(point)
            for point, sign in zip(coordinates, signs, strict=True)
        ]
        target = curve.sum(signed)
        if target is None:
            continue
        replay = curve.sum(signed)
        return {
            "event": "constructed_control",
            "cell_id": cell_id(curve_id_value, arm, seed),
            "attempt": attempt,
            "role": role,
            "indices": indices,
            "signs": signs,
            "points": [point_json(point) for point in coordinates],
            "constructed_target": point_json(target),
            "replay_pass": replay == target,
            "included_in_primary": False,
        }
    raise AssertionError("constructed-control stream exhausted")


def current_git_head() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise AuthorizationError("cannot resolve current Git HEAD") from error
    return result.stdout.strip()


def require_strict_ancestor(ancestor: str, descendant: str) -> None:
    if ancestor == descendant:
        raise AuthorizationError(
            "authorization must be merged after the readiness source commit"
        )
    try:
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, descendant],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
        )
    except OSError as error:
        raise AuthorizationError("cannot inspect Git ancestry") from error
    if result.returncode != 0:
        raise AuthorizationError(
            "readiness source commit is not an ancestor of current HEAD"
        )


def file_bytes_at_commit(commit: str, relative_path: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "show", f"{commit}:{relative_path}"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise AuthorizationError(
            f"cannot read {relative_path} at commit {commit}"
        ) from error
    return result.stdout


def require_execution_authorization(
    config: dict[str, Any],
    config_path: Path,
    curve_table_path: Path,
    *,
    authorization_not_after: datetime,
) -> dict[str, Any]:
    if config_path.resolve() != DEFAULT_CONFIG.resolve():
        raise AuthorizationError("execution requires the canonical config path")
    if curve_table_path.resolve() != DEFAULT_CURVE_TABLE.resolve():
        raise AuthorizationError(
            "execution requires the canonical curve-table path"
        )
    substrate = load_json(DEFAULT_AUTHORIZATION_SUBSTRATE)
    if not isinstance(substrate, dict):
        raise AuthorizationError(
            "canonical authorization substrate is not an object"
        )
    authorization = substrate.get(AUTHORIZATION_KEY)
    if not isinstance(authorization, dict):
        raise AuthorizationError(
            "canonical singleton authorization is absent"
        )
    expected_keys = {
        "status",
        "hypothesis_id",
        "task_id",
        "route_id",
        "cell_id",
        "promotion_authorized",
        "authorization_id",
        "source_commit",
        "authorized_utc",
        "sha256_bindings",
        "resource_budget",
        "scope",
    }
    if set(authorization) != expected_keys:
        raise AuthorizationError(
            "authorization singleton has an unexpected field set"
        )
    expected_identity = {
        "status": "approved",
        "hypothesis_id": HYPOTHESIS_ID,
        "task_id": TASK_ID,
        "route_id": ROUTE_ID,
        "cell_id": CELL_ID,
        "promotion_authorized": False,
    }
    for key, expected in expected_identity.items():
        if authorization.get(key) != expected:
            raise AuthorizationError(
                f"authorization {key} does not equal {expected!r}"
            )
    source_commit = authorization.get("source_commit")
    if (
        not isinstance(source_commit, str)
        or len(source_commit) != 40
        or any(character not in "0123456789abcdef" for character in source_commit)
    ):
        raise AuthorizationError("authorization has no exact source commit")
    authorization_id = authorization.get("authorization_id")
    if not isinstance(authorization_id, str) or not authorization_id:
        raise AuthorizationError("authorization has no authorization_id")
    authorized_utc = authorization.get("authorized_utc")
    if not isinstance(authorized_utc, str) or not authorized_utc.endswith("Z"):
        raise AuthorizationError("authorization has no authorized_utc")
    try:
        parsed_authorized_utc = datetime.fromisoformat(
            authorized_utc.replace("Z", "+00:00")
        )
    except ValueError as error:
        raise AuthorizationError("authorized_utc is not an ISO timestamp") from error
    if parsed_authorized_utc.utcoffset() != timezone.utc.utcoffset(
        parsed_authorized_utc
    ):
        raise AuthorizationError("authorized_utc is not canonical UTC")
    if parsed_authorized_utc > authorization_not_after:
        raise AuthorizationError("authorization timestamp is in the future")
    current_head = current_git_head()
    require_strict_ancestor(source_commit, current_head)
    substrate_relative = DEFAULT_AUTHORIZATION_SUBSTRATE.relative_to(
        REPO_ROOT
    ).as_posix()
    if sha256_bytes(
        file_bytes_at_commit(current_head, substrate_relative)
    ) != sha256_file(DEFAULT_AUTHORIZATION_SUBSTRATE):
        raise AuthorizationError(
            "canonical authorization substrate has uncommitted changes"
        )
    try:
        source_substrate = json.loads(
            file_bytes_at_commit(source_commit, substrate_relative)
        )
    except (AuthorizationError, json.JSONDecodeError) as error:
        raise AuthorizationError(
            "cannot inspect readiness-source authorization substrate"
        ) from error
    if not isinstance(source_substrate, dict):
        raise AuthorizationError(
            "readiness-source authorization substrate is not an object"
        )
    source_authorization = source_substrate.get(AUTHORIZATION_KEY)
    if source_authorization is not None and not isinstance(
        source_authorization, dict
    ):
        raise AuthorizationError(
            "readiness-source authorization singleton is malformed"
        )
    if (
        isinstance(source_authorization, dict)
        and source_authorization.get("status") == "approved"
    ):
        raise AuthorizationError(
            "readiness source already contained an approved authorization"
        )
    bindings = authorization.get("sha256_bindings")
    if not isinstance(bindings, dict):
        raise AuthorizationError("authorization has no SHA-256 bindings")
    bound_paths = {
        "preregistration": DEFAULT_PREREGISTRATION,
        "curve_table": curve_table_path,
        "experiment_config": config_path,
        "run_py": Path(__file__).resolve(),
        "validate_py": DEFAULT_VALIDATOR,
    }
    if set(bindings) != set(bound_paths):
        raise AuthorizationError("authorization binds the wrong file set")
    for key, path in bound_paths.items():
        if not path.is_file():
            raise AuthorizationError(f"bound file is absent: {path}")
        digest = sha256_file(path)
        if bindings.get(key) != digest:
            raise AuthorizationError(f"authorization hash mismatch: {key}")
        relative = path.relative_to(REPO_ROOT).as_posix()
        try:
            committed_digest = sha256_bytes(
                file_bytes_at_commit(source_commit, relative)
            )
        except AuthorizationError as error:
            raise AuthorizationError(
                f"{relative} is not present at readiness source commit"
            ) from error
        if committed_digest != digest:
            raise AuthorizationError(
                f"{relative} differs from readiness source commit"
            )
    if authorization.get("resource_budget") != config.get("resource_budget"):
        raise AuthorizationError("authorization budget mismatch")
    expected_scope = {
        "kind": "synthetic_toy_only",
        "curve_family": "E_7",
        "curve_ids": config["curve_ids"],
        "max_field_bits": 25,
        "real_world_targets_forbidden": True,
        "secp256k1_targets_forbidden": True,
    }
    if authorization.get("scope") != expected_scope:
        raise AuthorizationError("authorization safety scope mismatch")
    return authorization


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def measure_resource_usage(
    started_cpu: float,
    started_wall: float,
) -> dict[str, float]:
    """Measure the scientific run through the current terminal decision.

    Final JSON serialization and hashing happen after the terminal decision
    and are intentionally not used to retroactively change its status.
    """
    peak_rss_gib = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (
        1024 * 1024
    )
    if sys.platform == "darwin":
        peak_rss_gib /= 1024
    return {
        "cpu_hours": (time.process_time() - started_cpu) / 3600,
        "wall_hours": (time.monotonic() - started_wall) / 3600,
        "peak_rss_gib": peak_rss_gib,
    }


def exceeded_resource_reason(
    usage: dict[str, float],
    budget: dict[str, int],
) -> str | None:
    if usage["cpu_hours"] > budget["max_cpu_hours"]:
        return "maximum CPU-hour budget reached"
    if usage["peak_rss_gib"] > budget["max_peak_rss_gib"]:
        return "maximum peak-RSS budget reached"
    if usage["wall_hours"] > budget["max_wall_hours"]:
        return "maximum wall-hour budget reached"
    return None


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.write(canonical_bytes(value))


def write_event(handle: TextIO, event: dict[str, Any]) -> None:
    handle.write(
        json.dumps(
            event,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    )


def build_run_header(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "event": "run_header",
        "raw_schema_version": RAW_SCHEMA_VERSION,
        **manifest,
    }


def execute_authorized(
    config_path: Path,
    curve_table_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    """Execute the frozen grid only after the exact canonical gate passes."""
    if output_dir.resolve() != HERE.resolve():
        raise AuthorizationError(
            "authorized execution requires the canonical experiment directory"
        )
    started_wall = time.monotonic()
    started_cpu = time.process_time()
    started_instant = datetime.now(timezone.utc)
    started_utc = started_instant.isoformat().replace("+00:00", "Z")
    (
        config,
        curve_rows,
        targets,
        base_builds,
        authorization,
    ) = authorized_preflight(
        config_path,
        curve_table_path,
        authorization_not_after=started_instant,
    )
    output_paths = [
        output_dir / config["output_contract"]["manifest"],
        output_dir / config["output_contract"]["raw_jsonl"],
        output_dir / config["output_contract"]["summary"],
        output_dir / config["output_contract"]["validated_artifact"],
        output_dir / config["output_contract"]["validated_sidecar"],
    ]
    existing_outputs = [path for path in output_paths if path.exists()]
    if existing_outputs:
        raise AuthorizationError(
            "refusing to overwrite existing run outputs: "
            + ", ".join(str(path) for path in existing_outputs)
        )

    # Authorization is checked before this first output mutation.
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / config["output_contract"]["raw_jsonl"]
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    run_id = authorization["authorization_id"]
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "hypothesis_id": HYPOTHESIS_ID,
        "authorization_id": authorization["authorization_id"],
        "authorization_source_commit": authorization["source_commit"],
        "bindings": {
            "preregistration_sha256": sha256_file(DEFAULT_PREREGISTRATION),
            "curve_table_sha256": sha256_file(curve_table_path),
            "experiment_config_sha256": sha256_file(config_path),
            "run_py_sha256": sha256_file(Path(__file__).resolve()),
            "validate_py_sha256": sha256_file(DEFAULT_VALIDATOR),
        },
        "chronology": {
            "base_manifest_frozen_sequence": 1,
            "targets_committed_sequence": 2,
            "leaves_started_sequence": 3,
            "run_started_utc": started_utc,
        },
    }
    write_json(output_dir / config["output_contract"]["manifest"], manifest)

    target_by_cell = {target["cell_id"]: target for target in targets}
    total_operations = OperationCounts()
    for built in base_builds.values():
        total_operations.absorb_mapping(built.operation_counts)
    cell_summaries: list[dict[str, Any]] = []
    total_primary_trials = 0
    resource_exhausted_reason: str | None = None

    with raw_path.open("w", encoding="utf-8", newline="\n") as raw:
        write_event(raw, build_run_header(manifest))
        for target_entry in targets:
            entry_cell = target_entry["cell_id"]
            curve_id_value = target_entry["curve_id"]
            arm = target_entry["arm"]
            seed = target_entry["seed"]
            row = curve_rows[curve_id_value]
            built = base_builds[entry_cell]
            target = parse_point(target_entry["point"], "target")
            if target is None:
                raise AssertionError("verified target became identity")
            shuffled_entry = target_by_cell[
                target_entry["shuffled_target_cell_id"]
            ]
            shuffled_target = parse_point(
                shuffled_entry["point"], "shuffled_target"
            )
            if shuffled_target is None:
                raise AssertionError("verified shuffled target became identity")
            counter = OperationCounts()
            curve = Curve(row["p"], 0, 7, counter)
            x_to_index = {
                point[0]: index
                for index, point in enumerate(built.points)
            }
            x_set = set(x_to_index)
            write_event(
                raw,
                {
                    "event": "base",
                    "cell_id": entry_cell,
                    "curve_id": curve_id_value,
                    "arm": arm,
                    "seed": seed,
                    "points": [point_json(point) for point in built.points],
                    "commitment": built.commitment,
                    "selection_counts": built.selection_counts,
                    "prng_blocks": built.prng_blocks,
                    "prng_rejected_blocks": built.prng_rejected_blocks,
                    "operation_counts": built.operation_counts,
                    "frozen_sequence": 1,
                },
            )
            write_event(
                raw,
                {
                    "event": "target",
                    **target_entry,
                    "target_base_x_collision": target[0] in x_set,
                    "frozen_sequence": 2,
                },
            )
            write_event(
                raw,
                constructed_target_control(
                    curve,
                    built.points,
                    curve_id_value,
                    arm,
                    seed,
                ),
            )
            leaf_stream = CounterPRNG(
                stream_domain(curve_id_value, arm, seed, "leaves")
            )
            random_label_stream = CounterPRNG(
                stream_domain(curve_id_value, arm, seed, "random-label")
            )
            attempts = config["trials_per_seed"][curve_id_value]
            counts = {
                "attempts": 0,
                "accepted": 0,
                "affine_regular": 0,
                "balanced_regular": 0,
                "residual_identity": 0,
                "residual_not_in_base": 0,
                "shuffled_accepted": 0,
                "shuffled_affine_regular": 0,
                "random_label_true": 0,
                "repeated_index_total": 0,
                "repeated_coordinate_total": 0,
                "target_coordinate_collision_total": 0,
            }
            prefix_failures = [0] * 6
            suffix_failures = [0] * 6
            base_endpoint_failures = 0
            final_endpoint_failures = 0
            for trial_index in range(attempts):
                if total_primary_trials >= config["resource_budget"][
                    "max_primary_trials"
                ]:
                    resource_exhausted_reason = (
                        "maximum primary-trial budget reached"
                    )
                    break
                result = sample_primary_trial(
                    curve,
                    built.points,
                    x_to_index,
                    target,
                    leaf_stream,
                )
                total_primary_trials += 1
                counts["attempts"] += 1
                if result.accepted:
                    counts["accepted"] += 1
                    labels = result.labels
                    if labels is None:
                        raise AssertionError("accepted row has no labels")
                    counts["affine_regular"] += int(labels["affine_regular"])
                    counts["balanced_regular"] += int(
                        labels["balanced_regular"]
                    )
                    counts["repeated_index_total"] += (
                        result.repeated_index_count
                    )
                    counts["repeated_coordinate_total"] += (
                        result.repeated_coordinate_count
                    )
                    counts["target_coordinate_collision_total"] += (
                        result.target_coordinate_collision_count
                    )
                    base_endpoint_failures += int(
                        not labels["base_endpoint_nonzero"]
                    )
                    final_endpoint_failures += int(
                        not labels["final_endpoint_nonzero"]
                    )
                    for index, value in enumerate(labels["prefix_nonzero"]):
                        prefix_failures[index] += int(not value)
                    for index, value in enumerate(labels["suffix_nonzero"]):
                        suffix_failures[index] += int(not value)
                    random_label = random_label_stream.randbelow(2) == 1
                    counts["random_label_true"] += int(random_label)
                    write_event(
                        raw,
                        {
                            "event": "accepted",
                            "cell_id": entry_cell,
                            "trial_index": trial_index,
                            "indices": result.indices,
                            "signs": result.signs,
                            "points": [
                                point_json(point)
                                for point in result.coordinates
                            ],
                            "target": point_json(target),
                            "labels": labels,
                            "permutations": permutation_controls(
                                curve,
                                result.coordinates,
                                target,
                                curve_id_value,
                                arm,
                                seed,
                                trial_index,
                                config["permutation_controls"],
                            ),
                            "random_label": random_label,
                            "repeated_index_count": (
                                result.repeated_index_count
                            ),
                            "repeated_coordinate_count": (
                                result.repeated_coordinate_count
                            ),
                            "target_coordinate_collision_count": (
                                result.target_coordinate_collision_count
                            ),
                            "operation_counts": result.operation_counts,
                        },
                    )
                else:
                    if result.rejection_reason not in (
                        "residual_identity",
                        "residual_not_in_base",
                    ):
                        raise AssertionError("unknown rejection reason")
                    counts[result.rejection_reason] += 1

                # Matched shuffled-target control reuses the exact sampled
                # first 15 signed leaves and never changes the primary row.
                residual_control = curve.subtract(
                    shuffled_target, result.partial_sum
                )
                indices15 = result.indices[:15]
                signs15 = result.signs[:15]
                if (
                    residual_control is not None
                    and residual_control[0] in x_set
                ):
                    final_index = x_to_index[residual_control[0]]
                    final_point = built.points[final_index]
                    if residual_control == final_point:
                        final_sign = 1
                    elif residual_control == curve.negate(final_point):
                        final_sign = -1
                    else:
                        raise AssertionError(
                            "shuffled residual x matched neither point sign"
                        )
                    control_indices = indices15 + [final_index]
                    control_signs = signs15 + [final_sign]
                    control_coordinates = [
                        built.points[index] for index in control_indices
                    ]
                    replay = curve.sum(
                        point if sign == 1 else curve.negate(point)
                        for point, sign in zip(
                            control_coordinates,
                            control_signs,
                            strict=True,
                        )
                    )
                    if replay != shuffled_target:
                        raise AssertionError(
                            "shuffled-target control replay failed"
                        )
                    control_labels = task025_labels(
                        curve, control_coordinates, shuffled_target
                    )
                    counts["shuffled_accepted"] += 1
                    counts["shuffled_affine_regular"] += int(
                        control_labels["affine_regular"]
                    )
                    write_event(
                        raw,
                        {
                            "event": "shuffled_accepted",
                            "cell_id": entry_cell,
                            "source_target_cell_id": (
                                target_entry["shuffled_target_cell_id"]
                            ),
                            "trial_index": trial_index,
                            "indices": control_indices,
                            "signs": control_signs,
                            "points": [
                                point_json(point)
                                for point in control_coordinates
                            ],
                            "target": point_json(shuffled_target),
                            "labels": control_labels,
                        },
                    )
                if trial_index % 1024 == 1023 or trial_index + 1 == attempts:
                    usage = measure_resource_usage(started_cpu, started_wall)
                    resource_exhausted_reason = exceeded_resource_reason(
                        usage, config["resource_budget"]
                    )
                    if resource_exhausted_reason is not None:
                        break

            summary = {
                "event": "cell_summary",
                "cell_id": entry_cell,
                "curve_id": curve_id_value,
                "m": row["m"],
                "arm": arm,
                "seed": seed,
                "planned_attempts": attempts,
                "cell_complete": counts["attempts"] == attempts,
                "counts": counts,
                "endpoint_failures": {
                    "base": base_endpoint_failures,
                    "final": final_endpoint_failures,
                },
                "prefix_failures": prefix_failures,
                "suffix_failures": suffix_failures,
                "leaf_prng_blocks": leaf_stream.counter,
                "leaf_prng_rejected_blocks": leaf_stream.rejected_blocks,
                "operation_counts": counter.snapshot(),
            }
            cell_summaries.append(summary)
            total_operations.absorb(counter)
            write_event(raw, summary)
            if resource_exhausted_reason is not None:
                break

        terminal_resource_usage = measure_resource_usage(
            started_cpu, started_wall
        )
        if resource_exhausted_reason is None:
            resource_exhausted_reason = exceeded_resource_reason(
                terminal_resource_usage,
                config["resource_budget"],
            )
        finished_utc = utc_now()
        terminal_status = (
            "PRODUCER_RESOURCE_EXHAUSTED_UNVALIDATED"
            if resource_exhausted_reason is not None
            else "PRODUCER_COMPLETE_UNVALIDATED"
        )
        run_summary_event = {
            "event": "run_summary",
            "run_id": run_id,
            "total_primary_trials": total_primary_trials,
            "cell_count": len(cell_summaries),
            "operation_counts": total_operations.snapshot(),
            "terminal_status": terminal_status,
            "resource_exhausted_reason": resource_exhausted_reason,
            "finished_utc": finished_utc,
        }
        write_event(raw, run_summary_event)

    raw_sha256 = sha256_file(raw_path)
    summary = {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "hypothesis_id": HYPOTHESIS_ID,
        "run_id": run_id,
        "bindings": manifest["bindings"],
        "chronology": {
            **manifest["chronology"],
            "run_finished_utc": finished_utc,
        },
        "raw_files": [
            {
                "path": config["output_contract"]["raw_jsonl"],
                "sha256": raw_sha256,
                "bytes": raw_path.stat().st_size,
            }
        ],
        "cells": cell_summaries,
        "totals": {
            "primary_trials": total_primary_trials,
            "operations": total_operations.snapshot(),
        },
        "resource_usage": terminal_resource_usage,
        "terminal_status": terminal_status,
        "resource_exhausted_reason": resource_exhausted_reason,
    }
    write_json(output_dir / config["output_contract"]["summary"], summary)
    return summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--check-readiness",
        action="store_true",
        help="verify frozen inputs without sampling a primary trial",
    )
    mode.add_argument(
        "--check-authorization",
        action="store_true",
        help=(
            "verify the exact canonical approved gate without writing output "
            "or sampling a primary trial"
        ),
    )
    mode.add_argument(
        "--execute",
        action="store_true",
        help="execute only after exact canonical authorization",
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument(
        "--curve-table", type=Path, default=DEFAULT_CURVE_TABLE
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help=(
            "required for --execute; must be the canonical experiment "
            "directory with no existing outcome paths"
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.check_readiness or args.check_authorization:
            if args.output_dir is not None:
                raise ReadinessError(
                    "pre-execution checks do not accept --output-dir"
                )
            if args.check_readiness:
                result = check_readiness(args.config, args.curve_table)
                prefix = "READINESS_PASS"
            else:
                result = check_authorization(args.config, args.curve_table)
                prefix = "AUTHORIZATION_PASS"
            print(prefix + " " + json.dumps(result, sort_keys=True))
            return 0
        if args.output_dir is None:
            raise AuthorizationError("--execute requires --output-dir")
        summary = execute_authorized(
            args.config, args.curve_table, args.output_dir
        )
        print(
            summary["terminal_status"] + " "
            + json.dumps(
                {
                    "run_id": summary["run_id"],
                    "primary_trials": summary["totals"]["primary_trials"],
                },
                sort_keys=True,
            )
        )
        return 0
    except (ReadinessError, AuthorizationError) as error:
        print(f"FAIL_CLOSED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
