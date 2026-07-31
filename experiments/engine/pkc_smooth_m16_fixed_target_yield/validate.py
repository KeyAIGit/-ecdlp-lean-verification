#!/usr/bin/env python3
"""Independent validator for HYP-M16-FIXED-TARGET-YIELD-001.

This module intentionally imports no producer code.  Its only inputs are the
frozen JSON files described by ``CONFIG_CONTRACT`` and the Python standard
library.  The command line is fail closed:

* ``PASS`` means that every scientific field was independently replayed;
* ``INCONCLUSIVE`` means that the outcome bundle does not exist yet;
* ``FAIL`` means that a present bundle violates the frozen contract.

A fully replayed resource-capped bundle is validation ``PASS`` with scientific
terminal ``PAUSE_INCONCLUSIVE`` and an explicit cause.

The readiness branch contains this validator before any outcome-producing run.
After a separately merged authorization, ``--authorization`` independently
replays the complete canonical pre-execution gate without writing output or
sampling a primary trial.  The small ``readiness_fixture`` mode is available
only through the Python API with ``allow_fixture=True``; the command line never
accepts it as evidence.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Iterable, Iterator, Sequence


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
CURVE_TABLE_PATH = HERE / "curve_table.json"
CONFIG_PATH = HERE / "experiment_config.json"
ARTIFACT_PATH = HERE / "artifact.json"
SIDECAR_PATH = HERE / "artifact.sha256"
MANIFEST_PATH = HERE / "run_manifest.json"
RAW_PATH = HERE / "raw" / "transcript.jsonl"
SUMMARY_PATH = HERE / "summary.json"

SCHEMA_VERSION = "keyai-m16-fixed-target-yield-v1"
CURVE_SCHEMA_VERSION = "keyai-m16-fixed-target-curve-table-v1"
HYPOTHESIS_ID = "HYP-M16-FIXED-TARGET-YIELD-001"
TASK_ID = "TASK-026"
ROUTE_ID = "R-PETIT-COMPOSED-MAPS"
RESEARCH_CELL_ID = "CELL-M-PKC-SMOOTH-M16"
ARTIFACT_ID = "PKC-SMOOTH-M16-FIXED-TARGET-YIELD-001"
ARTIFACT_KIND = "fixed_target_yield_experiment"
ARTIFACT_SCHEMA_VERSION = "keyai-m16-fixed-target-validated-artifact-v1"
FIXTURE_KIND = "readiness_fixture"
PRNG_PREFIX = (
    b"KEYAI-HYP-M16-FIXED-TARGET-YIELD-001/sha256-counter-v1\x00"
)

ARMS = ("GLV_ORBIT_CLOSED", "PLAIN_MATCHED")
TERMINAL_STATUSES = {
    "PROMOTE_TO_SOLVER_SLOPE_TEST",
    "CLASSIFY_AS_KNOWN_LOCAL_SIMPLIFICATION",
    "KILL_AFFINE_M16_CONTINUATION",
    "PAUSE_INCONCLUSIVE",
    "REJECT_AS_ARTIFACT",
}
VALIDATION_STATUSES = {"PASS", "FAIL", "INCONCLUSIVE"}

EXPECTED_CURVES: tuple[dict[str, Any], ...] = (
    {
        "curve_id": "E7-P262153-N262567",
        "m": 19,
        "p": 262153,
        "field_bits": 19,
        "declared_order": 262567,
        "n": 262567,
        "cofactor": 1,
        "generator": {"x": 1, "y": 135720},
        "beta": 217087,
        "lambda": 191707,
        "certificate": {
            "hasse_deviation": 413,
            "hasse_deviation_squared": 170569,
            "four_p": 1048612,
            "n_squared": 68941429489,
            "sixteen_p": 4194448,
        },
    },
    {
        "curve_id": "E7-P1048783-N1050337",
        "m": 21,
        "p": 1048783,
        "field_bits": 21,
        "declared_order": 1050337,
        "n": 1050337,
        "cofactor": 1,
        "generator": {"x": 1, "y": 558043},
        "beta": 858341,
        "lambda": 484979,
        "certificate": {
            "hasse_deviation": 1553,
            "hasse_deviation_squared": 2411809,
            "four_p": 4195132,
            "n_squared": 1103207813569,
            "sixteen_p": 16780528,
        },
    },
    {
        "curve_id": "E7-P16777711-N5591281",
        "m": 23,
        "p": 16777711,
        "field_bits": 25,
        "declared_order": 16773843,
        "n": 5591281,
        "cofactor": 3,
        "generator": {"x": 8760145, "y": 10159998},
        "beta": 3243663,
        "lambda": 4073091,
        "certificate": {
            "hasse_deviation": -3869,
            "hasse_deviation_squared": 14969161,
            "four_p": 67110844,
            "n_squared": 31262423220961,
            "sixteen_p": 268443376,
        },
    },
)

UPSTREAM_BINDINGS = {
    "experiments/engine/pkc_smooth_m16_exceptional_fibers/artifact.json":
        "578db732807a452e26de03dcd338d62c25a7d90490a62bbf427b1f96c3a869cf",
    "experiments/engine/pkc_smooth_m16_frozen_projective_witness/artifact.json":
        "89c645545d89334473d51654a41ff7ec2364857d034c64ce08d505337fa1e2d4",
    "experiments/engine/pkc_smooth_m16_infinity_propagation/artifact.json":
        "9330603ba1f0af9ee4902c263200709e2ec6f8c50d8d7eaab3b55bcba78e388f",
    "Ecdlp/Proved/FrozenRecursiveProjectiveWitness.lean":
        "5cffb444d95f7691f92bfbd094d945be7e97069edb244d5234fa06f359a852b9",
    "Ecdlp/Proved/FrozenProjectiveInfinityPropagation.lean":
        "7f868aab5b946a55a213ce26a461477321d6387830eed218c414f1e62853b4b4",
    "experiments/framework/ec_oracle.py":
        "7acc852df5a927a7954f56bd9548ec021ef0b0c92f5435e8f213363f71c72792",
}

# Frozen external JSON contract.  It is duplicated here instead of being
# imported from run.py so that a producer change cannot silently change the
# verifier semantics.
CONFIG_CONTRACT = {
    "schema_version": SCHEMA_VERSION,
    "hypothesis_id": HYPOTHESIS_ID,
    "curve_model": {"a": 0, "b": 7},
    "factor_base_size": 384,
    "orbit_seed_count": 128,
    "seeds": [101, 211, 307, 401, 503],
    "permutations_per_accepted": 16,
    "wilson_z": 1.959963984540054,
    "minimum_accepted": 100,
    "promotion_lower_bound": 0.90,
    "kill_upper_bound": 0.80,
    "maximum_decline": 0.05,
    "known_delta": 0.05,
    "new_mechanism_delta": 0.10,
}

DECISION_THRESHOLDS = {
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
}

Point = tuple[int, int] | None


class ValidationFailure(Exception):
    """A scientific or integrity check failed."""


class ValidationInconclusive(Exception):
    """Required run outputs are not present yet."""


class Replay:
    """Collect explicit validation causes while failing closed."""

    def __init__(self) -> None:
        self.checks = 0

    def require(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            raise ValidationFailure(message)

    def exact(self, label: str, actual: Any, expected: Any) -> None:
        self.require(actual == expected, f"{label}: {actual!r} != {expected!r}")


class CounterPrng:
    """Frozen SHA-256 counter stream, independently implemented."""

    def __init__(self, prefix: bytes, domain: str) -> None:
        domain_bytes = domain.encode("utf-8")
        self._stem = (
            prefix
            + len(domain_bytes).to_bytes(4, "big")
            + domain_bytes
        )
        self.counter = 0
        self.rejected_blocks = 0

    def word(self) -> int:
        if self.counter >= 1 << 128:
            raise ValidationFailure("PRNG counter exhausted")
        digest = hashlib.sha256(
            self._stem + self.counter.to_bytes(16, "big")
        ).digest()
        self.counter += 1
        return int.from_bytes(digest, "big")

    def randbelow(self, bound: int) -> int:
        if not isinstance(bound, int) or bound <= 0:
            raise ValidationFailure("randbelow bound must be positive")
        limit = ((1 << 256) // bound) * bound
        while True:
            candidate = self.word()
            if candidate < limit:
                return candidate % bound
            self.rejected_blocks += 1


def prng_domain(
    curve_id: str, arm: str, seed: int, role: str
) -> str:
    return f"{HYPOTHESIS_ID}/{curve_id}/{arm}/{seed}/{role}"


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        .encode("ascii")
    )


def canonical_utf8_line(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value) + b"\n").hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_sidecar(artifact_path: Path, sidecar_path: Path, replay: Replay) -> None:
    try:
        fields = sidecar_path.read_text(encoding="utf-8").strip().split()
    except OSError as exc:
        raise ValidationFailure(f"cannot read {sidecar_path}: {exc}") from exc
    replay.require(bool(fields), "empty artifact.sha256")
    replay.exact("artifact sidecar digest", fields[0], file_sha256(artifact_path))
    if len(fields) > 1:
        replay.exact("artifact sidecar filename", fields[1], artifact_path.name)


VALIDATION_CHECK_FAMILIES = (
    "curve-order-and-glv-certificates",
    "factor-base-reconstruction-and-commitments",
    "paired-public-target-reconstruction-and-chronology",
    "accepted-exact-ec-relations",
    "endpoints-and-twelve-signed-zero-obstructions",
    "permutation-random-label-shuffled-and-constructed-controls",
    "wilson-intervals-and-precommitted-decisions",
    "raw-canonical-order-hashes-and-summary-replay",
    "operation-count-and-resource-terminal-replay",
    "authorization-scope-bindings-and-git-ancestry",
    "upstream-artifact-and-lean-source-bindings",
)

CLAIM_BOUNDARY = {
    "evidence_scope": "synthetic-toy-E7-curves-only",
    "real_world_targets_used": False,
    "secp256k1_targets_used": False,
    "secp256k1_key_recovery_claim": False,
    "secp256k1_attack_claim": False,
    "asymptotic_improvement_claim": False,
    "promotion_authorized": False,
    "maximum_positive_interpretation": (
        "one separately preregistered solver-slope proposal"
    ),
    "h_new_interpretation": (
        "POTENTIALLY NOVEL / NOVELTY UNVERIFIED; not an attack promotion"
    ),
}


def serialize_curve_arm_metrics(
    metrics: dict[tuple[str, str], dict[str, Any]]
) -> list[dict[str, Any]]:
    rows = [
        {"curve_id": curve_id, "arm": arm, **value}
        for (curve_id, arm), value in metrics.items()
    ]
    curve_order = tuple(curve["curve_id"] for curve in EXPECTED_CURVES)
    rows.sort(
        key=lambda row: (
            curve_order.index(row["curve_id"]),
            ARMS.index(row["arm"]),
        )
    )
    return rows


def build_validated_artifact(
    *,
    report: dict[str, Any],
    manifest: dict[str, Any],
    summary: dict[str, Any],
    config: dict[str, Any],
    manifest_path: Path,
    raw_path: Path,
    summary_path: Path,
) -> dict[str, Any]:
    """Build the deterministic validator-owned scientific receipt."""

    substrate_path = REPO_ROOT / config["authorization_contract"]["path"]
    substrate = load_json(substrate_path)
    authorization = substrate.get(
        config["authorization_contract"]["singleton_key"]
    )
    if not isinstance(authorization, dict):
        raise ValidationFailure("validated artifact lacks authorization")
    raw_binding = summary["raw_files"]
    if not isinstance(raw_binding, list) or len(raw_binding) != 1:
        raise ValidationFailure("validated artifact requires one raw binding")
    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "artifact_kind": ARTIFACT_KIND,
        "hypothesis_id": HYPOTHESIS_ID,
        "task_id": TASK_ID,
        "route_id": ROUTE_ID,
        "research_cell_id": RESEARCH_CELL_ID,
        "run_id": manifest["run_id"],
        "validation": {
            "status": report["validation_status"],
            "independent_checks": report["checks"],
            "check_families": list(VALIDATION_CHECK_FAMILIES),
            "validator_sha256": file_sha256(Path(__file__).resolve()),
        },
        "terminal_status": report["terminal_status"],
        "terminal_cause": report.get("cause"),
        "opens_solver_slope_proposal":
            report["opens_solver_slope_proposal"],
        "h_new_retained": report["h_new_retained"],
        "curve_arm_metrics": serialize_curve_arm_metrics(
            report["curve_arm_metrics"]
        ),
        "decision_metrics": report["decision_metrics"],
        "bindings": {
            "authorization": authorization,
            "producer_inputs": manifest["bindings"],
            "run_manifest": {
                "path": manifest_path.name,
                "sha256": file_sha256(manifest_path),
                "bytes": manifest_path.stat().st_size,
            },
            "raw_files": raw_binding,
            "raw_transcript_replayed_sha256": file_sha256(raw_path),
            "summary": {
                "path": summary_path.name,
                "sha256": file_sha256(summary_path),
                "bytes": summary_path.stat().st_size,
            },
            "upstream": UPSTREAM_BINDINGS,
        },
        "chronology": summary["chronology"],
        "resource_usage": summary["resource_usage"],
        "claim_boundary": CLAIM_BOUNDARY,
    }


def verify_validated_artifact(
    expected: dict[str, Any],
    artifact_path: Path,
    sidecar_path: Path,
    replay: Replay,
) -> None:
    replay.require(artifact_path.is_file(), "validated artifact is missing")
    replay.require(sidecar_path.is_file(), "validated sidecar is missing")
    replay.exact(
        "validated artifact canonical bytes",
        artifact_path.read_bytes(),
        canonical_utf8_line(expected),
    )
    expected_sidecar = (
        file_sha256(artifact_path)
        + "  "
        + artifact_path.name
        + "\n"
    ).encode("ascii")
    replay.exact(
        "validated artifact sidecar bytes",
        sidecar_path.read_bytes(),
        expected_sidecar,
    )


def emit_validated_artifact(
    document: dict[str, Any],
    artifact_path: Path,
    sidecar_path: Path,
) -> None:
    """Create an immutable receipt and hash sidecar, refusing overwrite."""

    if artifact_path.exists() or sidecar_path.exists():
        raise ValidationFailure(
            "refusing to overwrite an existing validated artifact or sidecar"
        )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_utf8_line(document)
    artifact_created = False
    sidecar_created = False
    try:
        with artifact_path.open("xb") as handle:
            handle.write(payload)
        artifact_created = True
        digest = hashlib.sha256(payload).hexdigest()
        with sidecar_path.open("xb") as handle:
            handle.write(
                f"{digest}  {artifact_path.name}\n".encode("ascii")
            )
        sidecar_created = True
    except Exception:
        # Roll back only files that this call itself created.
        if sidecar_created:
            sidecar_path.unlink()
        if artifact_created:
            artifact_path.unlink()
        raise


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationFailure(f"cannot parse {path}: {exc}") from exc


def parse_utc_timestamp(value: Any, label: str, replay: Replay) -> datetime:
    replay.require(
        isinstance(value, str) and value.endswith("Z"),
        f"{label}: expected UTC timestamp ending in Z",
    )
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValidationFailure(f"{label}: invalid timestamp") from exc
    replay.exact(f"{label}.timezone", parsed.tzinfo, timezone.utc)
    return parsed


def parse_point(value: Any, label: str, replay: Replay) -> Point:
    replay.require(
        isinstance(value, dict)
        and set(value) == {"x", "y"}
        and all(
            isinstance(value[coordinate], int)
            and not isinstance(value[coordinate], bool)
            for coordinate in ("x", "y")
        ),
        f"{label}: expected {{x,y}} integer point",
    )
    return (value["x"], value["y"])


def point_json(point: Point) -> dict[str, int] | None:
    return None if point is None else {"x": point[0], "y": point[1]}


def is_probable_prime_64(n: int) -> bool:
    """Deterministic Miller-Rabin for unsigned 64-bit integers."""

    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for prime in small:
        if n % prime == 0:
            return n == prime
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for base in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if base % n == 0:
            continue
        x = pow(base, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def inv_mod(value: int, p: int) -> int:
    if value % p == 0:
        raise ValidationFailure("attempted inversion of zero")
    return pow(value, -1, p)


def on_curve(point: Point, p: int) -> bool:
    if point is None:
        return True
    x, y = point
    return 0 <= x < p and 0 <= y < p and y * y % p == (x * x * x + 7) % p


def ec_neg(point: Point, p: int) -> Point:
    if point is None:
        return None
    return (point[0], (-point[1]) % p)


def ec_add(left: Point, right: Point, p: int) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if left == right:
        if y1 % p == 0:
            return None
        slope = 3 * x1 * x1 * inv_mod(2 * y1, p) % p
    else:
        slope = (y2 - y1) * inv_mod(x2 - x1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return (x3, y3)


def ec_sub(left: Point, right: Point, p: int) -> Point:
    return ec_add(left, ec_neg(right, p), p)


def ec_mul(scalar: int, point: Point, p: int) -> Point:
    if scalar < 0:
        return ec_mul(-scalar, ec_neg(point, p), p)
    result: Point = None
    addend = point
    while scalar:
        if scalar & 1:
            result = ec_add(result, addend, p)
        addend = ec_add(addend, addend, p)
        scalar >>= 1
    return result


def ec_sum(points: Iterable[Point], p: int) -> Point:
    result: Point = None
    for point in points:
        result = ec_add(result, point, p)
    return result


def zero_operation_counts() -> dict[str, int]:
    return {
        "curve_additions": 0,
        "curve_doublings": 0,
        "identity_shortcuts": 0,
        "field_inversions": 0,
        "scalar_multiplication_bits": 0,
    }


def counted_ec_add(
    left: Point, right: Point, p: int, counts: dict[str, int]
) -> Point:
    if left is None:
        counts["identity_shortcuts"] += 1
        return right
    if right is None:
        counts["identity_shortcuts"] += 1
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        counts["curve_additions"] += 1
        return None
    if left == right:
        counts["curve_doublings"] += 1
        denominator = 2 * y1 % p
        if denominator == 0:
            return None
        numerator = 3 * x1 * x1 % p
    else:
        counts["curve_additions"] += 1
        denominator = (x2 - x1) % p
        if denominator == 0:
            return None
        numerator = (y2 - y1) % p
    counts["field_inversions"] += 1
    slope = numerator * pow(denominator, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return (x3, y3)


def counted_ec_mul(
    scalar: int, point: Point, p: int, counts: dict[str, int]
) -> Point:
    counts["scalar_multiplication_bits"] += scalar.bit_length()
    result: Point = None
    addend = point
    remaining = scalar
    while remaining:
        if remaining & 1:
            result = counted_ec_add(result, addend, p, counts)
        remaining >>= 1
        if remaining:
            addend = counted_ec_add(addend, addend, p, counts)
    return result


def signed_zero_obstruction(points: Sequence[Point], p: int) -> bool:
    """Return True exactly when some independent sign choice sums to O."""

    states: set[Point] = {None}
    for point in points:
        negative = ec_neg(point, p)
        states = {
            candidate
            for state in states
            for candidate in (ec_add(state, point, p), ec_add(state, negative, p))
        }
    return None in states


def regularity_labels(
    points: Sequence[Point], target: Point, p: int
) -> dict[str, Any]:
    if len(points) != 16 or target is None or any(point is None for point in points):
        raise ValidationFailure("regularity requires 16 affine points and affine target")
    affine_points = [point for point in points if point is not None]
    prefix_nonzero = [
        not signed_zero_obstruction(affine_points[0:j + 3], p) for j in range(6)
    ]
    suffix_nonzero = [
        not signed_zero_obstruction(
            [target] + affine_points[14 - j:16],
            p,
        )
        for j in range(6)
    ]
    base_endpoint = affine_points[0][0] != affine_points[1][0]
    final_endpoint = affine_points[15][0] != target[0]
    balanced = all(prefix_nonzero) and all(suffix_nonzero)
    return {
        "base_endpoint_nonzero": base_endpoint,
        "final_endpoint_nonzero": final_endpoint,
        "prefix_nonzero": prefix_nonzero,
        "suffix_nonzero": suffix_nonzero,
        "balanced_regular": balanced,
        "affine_regular": base_endpoint and final_endpoint and balanced,
    }


def wilson_interval(successes: int, trials: int) -> tuple[float, float]:
    if not (
        isinstance(successes, int)
        and isinstance(trials, int)
        and 0 <= successes <= trials
    ):
        raise ValidationFailure("invalid binomial counts")
    if trials == 0:
        return (0.0, 1.0)
    z = CONFIG_CONTRACT["wilson_z"]
    denominator = 1.0 + z * z / trials
    center = (successes / trials + z * z / (2.0 * trials)) / denominator
    radius = (
        z
        * math.sqrt(
            successes / trials * (1.0 - successes / trials) / trials
            + z * z / (4.0 * trials * trials)
        )
        / denominator
    )
    return (center - radius, center + radius)


def rounded_interval(successes: int, trials: int) -> list[float]:
    return [round(value, 15) for value in wilson_interval(successes, trials)]


def check_curve_row(row: dict[str, Any], expected: dict[str, Any], replay: Replay) -> None:
    replay.exact(f"{expected['curve_id']}.row", row, expected)
    p = row["p"]
    n = row["n"]
    total = row["declared_order"]
    h = row["cofactor"]
    generator = parse_point(row["generator"], f"{row['curve_id']}.generator", replay)
    replay.require(is_probable_prime_64(p), f"{row['curve_id']}: p is not prime")
    replay.require(is_probable_prime_64(n), f"{row['curve_id']}: n is not prime")
    replay.exact(f"{row['curve_id']}.field_bits", p.bit_length(), row["field_bits"])
    replay.exact(f"{row['curve_id']}.m", (n - 1).bit_length(), row["m"])
    replay.exact(f"{row['curve_id']}.N", h * n, total)
    replay.require(generator is not None, f"{row['curve_id']}: G is infinity")
    replay.require(on_curve(generator, p), f"{row['curve_id']}: G is off curve")
    replay.exact(f"{row['curve_id']}.[n]G", ec_mul(n, generator, p), None)

    # Exact integer Hasse certificate.  Since G has prime order n, n divides
    # #E.  The declared multiple h*n is in the Hasse interval and both adjacent
    # multiples are outside, so it is the unique possible group order.
    delta = total - (p + 1)
    replay.require(
        n * n > 16 * p,
        f"{row['curve_id']}: subgroup order does not isolate one Hasse multiple",
    )
    replay.require(
        delta * delta <= 4 * p,
        f"{row['curve_id']}: declared order outside Hasse interval",
    )
    replay.require(
        (delta + n) * (delta + n) > 4 * p,
        f"{row['curve_id']}: lower adjacent multiple remains in Hasse interval",
    )
    replay.require(
        (delta - n) * (delta - n) > 4 * p,
        f"{row['curve_id']}: upper adjacent multiple remains in Hasse interval",
    )
    replay.exact(
        f"{row['curve_id']}.certificate",
        row["certificate"],
        {
            "hasse_deviation": delta,
            "hasse_deviation_squared": delta * delta,
            "four_p": 4 * p,
            "n_squared": n * n,
            "sixteen_p": 16 * p,
        },
    )

    beta = row["beta"]
    eigenvalue = row["lambda"]
    replay.exact(f"{row['curve_id']}.beta^3", pow(beta, 3, p), 1)
    replay.require(beta % p != 1, f"{row['curve_id']}: beta is trivial")
    replay.exact(
        f"{row['curve_id']}.lambda polynomial",
        (eigenvalue * eigenvalue + eigenvalue + 1) % n,
        0,
    )
    phi_generator = (beta * generator[0] % p, generator[1])
    replay.require(on_curve(phi_generator, p), f"{row['curve_id']}: phi(G) off curve")
    replay.exact(
        f"{row['curve_id']}.eigenvalue",
        ec_mul(eigenvalue, generator, p),
        phi_generator,
    )


def check_curve_table(document: Any, replay: Replay) -> dict[str, dict[str, Any]]:
    replay.require(isinstance(document, dict), "curve_table: expected object")
    replay.exact("curve_table.schema_version", document.get("schema_version"),
                 CURVE_SCHEMA_VERSION)
    replay.exact("curve_table.hypothesis_id", document.get("hypothesis_id"),
                 HYPOTHESIS_ID)
    replay.exact(
        "curve_table.curve_family",
        document.get("curve_family"),
        {
            "a": 0,
            "b": 7,
            "equation": "y^2 = x^3 + 7",
            "field": "prime",
        },
    )
    replay.exact(
        "curve_table.order_certificate_contract",
        document.get("order_certificate_contract"),
        {
            "method": "prime_subgroup_hasse_unique_multiple",
            "checks": [
                "p and n are prime",
                "G is a nonidentity point on E_7",
                "[n]G is the identity, hence ord(G)=n",
                "n^2 > 16*p, hence the Hasse interval has width strictly less than n",
                "(declared_order-(p+1))^2 <= 4*p",
                "declared_order = cofactor*n",
            ],
            "conclusion": (
                "The unique multiple of n in the Hasse interval is "
                "declared_order, so #E(F_p)=declared_order exactly."
            ),
        },
    )
    rows = document.get("curves")
    replay.require(isinstance(rows, list), "curve_table.curves: expected list")
    replay.exact("curve_table.curve count", len(rows), len(EXPECTED_CURVES))
    result: dict[str, dict[str, Any]] = {}
    for row, expected in zip(rows, EXPECTED_CURVES):
        replay.require(isinstance(row, dict), "curve_table row: expected object")
        check_curve_row(row, expected, replay)
        result[row["curve_id"]] = row
    return result


def check_config(
    document: Any,
    curves: dict[str, dict[str, Any]],
    replay: Replay,
    *,
    curve_table_path: Path,
    preregistration_path: Path,
) -> tuple[dict[str, list[Point]], dict[str, dict[str, Any]]]:
    replay.require(isinstance(document, dict), "config: expected object")
    replay.exact(
        "config top-level keys",
        set(document),
        {
            "schema_version",
            "hypothesis_id",
            "task_id",
            "route_id",
            "cell_id",
            "preregistration_sha256",
            "curve_table_sha256",
            "curve_ids",
            "arms",
            "seeds",
            "trials_per_seed",
            "factor_base_size",
            "relation_arity",
            "sampled_leaves_per_trial",
            "permutation_controls",
            "prng",
            "factor_base_contract",
            "target_generation_contract",
            "chronology_contract",
            "base_manifest",
            "targets",
            "label_contract",
            "controls",
            "decision_thresholds",
            "resource_budget",
            "authorization_contract",
            "output_contract",
        },
    )
    replay.exact(
        "config.schema_version",
        document.get("schema_version"),
        "keyai-m16-fixed-target-config-v1",
    )
    for key, expected in {
        "hypothesis_id": HYPOTHESIS_ID,
        "task_id": TASK_ID,
        "route_id": ROUTE_ID,
        "cell_id": RESEARCH_CELL_ID,
        "factor_base_size": 384,
        "relation_arity": 16,
        "sampled_leaves_per_trial": 15,
        "permutation_controls": 16,
    }.items():
        replay.exact(f"config.{key}", document.get(key), expected)
    replay.exact(
        "config.preregistration_sha256",
        document.get("preregistration_sha256"),
        file_sha256(preregistration_path),
    )
    replay.exact(
        "config.curve_table_sha256",
        document.get("curve_table_sha256"),
        file_sha256(curve_table_path),
    )
    replay.exact("config.curve_ids", document.get("curve_ids"), list(curves))
    replay.exact("config.arms", document.get("arms"), list(ARMS))
    seeds = document.get("seeds")
    replay.require(
        isinstance(seeds, list)
        and len(seeds) == 5
        and len(set(seeds)) == 5
        and all(isinstance(seed, int) and not isinstance(seed, bool)
                for seed in seeds),
        "config.seeds: expected five distinct integers",
    )
    replay.exact("config.seeds frozen order", seeds, CONFIG_CONTRACT["seeds"])
    replay.exact(
        "config.trials_per_seed",
        document.get("trials_per_seed"),
        {
            "E7-P262153-N262567": 10000,
            "E7-P1048783-N1050337": 40000,
            "E7-P16777711-N5591281": 250000,
        },
    )
    replay.exact(
        "config.resource_budget",
        document.get("resource_budget"),
        {
            "max_primary_trials": 3000000,
            "max_cpu_hours": 4,
            "max_peak_rss_gib": 4,
            "max_wall_hours": 24,
        },
    )
    replay.exact(
        "config.prng",
        document.get("prng"),
        {
            "algorithm": "sha256-counter-rejection-v1",
            "prefix_hex": PRNG_PREFIX.hex(),
            "counter_bytes": 16,
            "counter_endian": "big",
            "domain_length_bytes": 4,
            "domain_length_endian": "big",
            "digest_integer_endian": "big",
            "randbelow": (
                "reject x >= 2^256-(2^256 mod bound), return x mod bound"
            ),
            "domain_template": (
                "HYP-M16-FIXED-TARGET-YIELD-001/{curve_id}/{arm}/"
                "{seed}/{role}"
            ),
        },
    )
    replay.exact(
        "config.factor_base_contract",
        document.get("factor_base_contract"),
        {
            "scalar_draw": "randbelow(n-1)+1",
            "point_sign_storage": (
                "the generated affine point is stored; a trial sign is "
                "sampled separately"
            ),
            "unique_x_required": True,
            "orbit_closed_order": ["P", "phi(P)", "phi^2(P)"],
            "plain_orbit_relations": "counted but retained",
            "commitment": (
                "SHA256(canonical compact sorted-key JSON plus LF of arm, "
                "cell_id, curve_id, ordered points, seed, and statement)"
            ),
        },
    )
    replay.exact(
        "config.chronology_contract",
        document.get("chronology_contract"),
        {
            "base_manifest_frozen_sequence": 1,
            "targets_committed_sequence": 2,
            "leaves_started_sequence": 3,
            "target_scalar_recorded": False,
            "target_generation_seed_exposed_to_sampler": False,
        },
    )
    replay.exact(
        "config.target_generation_contract",
        document.get("target_generation_contract"),
        {
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
        },
    )
    replay.exact(
        "config.label_contract",
        document.get("label_contract"),
        {
            "prefix_ranges": [[0, end] for end in range(3, 9)],
            "suffix_ranges_after_target": [
                [start, 16] for start in range(14, 8, -1)
            ],
            "signed_zero_rule": (
                "start with {O}; replace states by unique S+P and S-P; "
                "obstruction is nonzero iff O is absent"
            ),
            "balanced_regular": (
                "all six prefix_nonzero and all six suffix_nonzero"
            ),
            "affine_regular": (
                "balanced_regular and both endpoint_nonzero labels"
            ),
        },
    )
    replay.exact(
        "config.controls",
        document.get("controls"),
        {
            "constructed_target_per_cell": 1,
            "constructed_target_in_primary": False,
            "constructed_target_role_template": "constructed-control/{attempt}",
            "random_label_role": "random-label",
            "shuffled_target_mapping": (
                "next seed cyclically within the same curve and arm"
            ),
            "fresh_held_out_seeds": True,
        },
    )
    replay.exact(
        "config.decision_thresholds",
        document.get("decision_thresholds"),
        DECISION_THRESHOLDS,
    )
    replay.exact(
        "config.authorization_contract",
        document.get("authorization_contract"),
        {
            "path": "repo/ECDLP_DECISION_SUBSTRATE.json",
            "singleton_key": "bounded_experiment_authorization",
            "required_status": "approved",
            "promotion_authorized": False,
        },
    )
    replay.exact(
        "config.output_contract",
        document.get("output_contract"),
        {
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
        },
    )

    manifest = document.get("base_manifest")
    replay.require(
        isinstance(manifest, list) and len(manifest) == 30,
        "config.base_manifest: expected 30 cells",
    )
    expected_grid = {
        (curve_id, arm, seed)
        for curve_id in curves
        for arm in ARMS
        for seed in seeds
    }
    prefix = bytes.fromhex(document["prng"]["prefix_hex"])
    bases: dict[str, list[Point]] = {}
    seen_grid: set[tuple[str, str, int]] = set()
    for entry in manifest:
        replay.require(isinstance(entry, dict), "base manifest entry object")
        replay.exact(
            "base manifest entry keys",
            set(entry),
            {
                "cell_id",
                "curve_id",
                "arm",
                "seed",
                "ordered_base_sha256",
                "frozen_sequence",
            },
        )
        key = (entry["curve_id"], entry["arm"], entry["seed"])
        replay.require(key in expected_grid, f"unknown base cell {key!r}")
        replay.require(key not in seen_grid, f"duplicate base cell {key!r}")
        seen_grid.add(key)
        expected_cell = f"{entry['curve_id']}--{entry['arm']}--S{entry['seed']}"
        replay.exact(f"{expected_cell}.cell_id", entry["cell_id"], expected_cell)
        replay.exact(f"{expected_cell}.frozen_sequence",
                     entry["frozen_sequence"], 1)
        points, _ = reconstruct_factor_base(
            curve=curves[entry["curve_id"]],
            arm=entry["arm"],
            seed=entry["seed"],
            prefix=prefix,
            size=document["factor_base_size"],
        )
        replay.exact(
            f"{expected_cell}.ordered_base_sha256",
            entry["ordered_base_sha256"],
            base_commitment(
                entry["curve_id"], entry["arm"], entry["seed"], points
            ),
        )
        bases[expected_cell] = points
    replay.exact("config.base grid", seen_grid, expected_grid)

    targets_raw = document.get("targets")
    replay.require(
        isinstance(targets_raw, list) and len(targets_raw) == 30,
        "config.targets: expected 30 cells",
    )
    targets: dict[str, dict[str, Any]] = {}
    for entry in targets_raw:
        replay.require(isinstance(entry, dict), "target manifest entry object")
        replay.exact(
            "target manifest entry keys",
            set(entry),
            {
                "cell_id",
                "curve_id",
                "arm",
                "seed",
                "point",
                "base_commitment",
                "commitment",
                "statement",
                "shuffled_target_cell_id",
                "frozen_sequence",
            },
        )
        current_cell = entry["cell_id"]
        replay.require(current_cell in bases, f"target without base: {current_cell}")
        replay.require(current_cell not in targets, f"duplicate target: {current_cell}")
        expected_cell = (
            f"{entry['curve_id']}--{entry['arm']}--S{entry['seed']}"
        )
        replay.exact(f"{current_cell}.target identity", current_cell, expected_cell)
        replay.exact(f"{current_cell}.target statement",
                     entry["statement"], "target-frozen-before-leaf-stream-v1")
        replay.exact(
            f"{current_cell}.target base commitment",
            entry["base_commitment"],
            next(
                base_entry["ordered_base_sha256"]
                for base_entry in manifest
                if base_entry["cell_id"] == current_cell
            ),
        )
        replay.exact(f"{current_cell}.target frozen sequence",
                     entry["frozen_sequence"], 2)
        replay.exact(
            f"{current_cell}.target commitment",
            entry["commitment"],
            target_commitment(entry),
        )
        target = parse_point(entry["point"], f"{current_cell}.target", replay)
        domains = {
            role: prng_domain(
                entry["curve_id"],
                "PAIRED_TARGET" if role == "target" else entry["arm"],
                entry["seed"],
                role,
            )
            for role in (
                "base",
                "target",
                "leaves",
                "random-label",
                "constructed-control/0",
                "permutation/0/0",
            )
        }
        replay.exact(
            f"{current_cell}.domain separation",
            len(set(domains.values())),
            len(domains),
        )
        replay.exact(
            f"{current_cell}.target public stream",
            target,
            reconstruct_target_point(
                curve=curves[entry["curve_id"]],
                seed=entry["seed"],
                prefix=prefix,
            ),
        )
        check_point_in_subgroup(
            target, curves[entry["curve_id"]], f"{current_cell}.target", replay
        )
        targets[current_cell] = entry
    replay.exact("config.target cells", set(targets), set(bases))
    paired_points: dict[tuple[str, int], Any] = {}
    for entry in targets.values():
        pair_key = (entry["curve_id"], entry["seed"])
        if pair_key in paired_points:
            replay.exact(
                f"{pair_key}.paired target identity",
                entry["point"],
                paired_points[pair_key],
            )
        else:
            paired_points[pair_key] = entry["point"]
    replay.exact("config paired target count", len(paired_points), 15)
    for entry in targets.values():
        shuffled = entry["shuffled_target_cell_id"]
        replay.require(shuffled in targets, "shuffled target references unknown cell")
        peer = targets[shuffled]
        replay.exact(
            f"{entry['cell_id']}.shuffled curve",
            peer["curve_id"],
            entry["curve_id"],
        )
        replay.exact(
            f"{entry['cell_id']}.shuffled arm",
            peer["arm"],
            entry["arm"],
        )
        replay.require(
            peer["seed"] != entry["seed"],
            f"{entry['cell_id']}: shuffled peer reuses seed",
        )
        seed_index = seeds.index(entry["seed"])
        expected_peer_seed = seeds[(seed_index + 1) % len(seeds)]
        expected_peer_cell = (
            f"{entry['curve_id']}--{entry['arm']}--S{expected_peer_seed}"
        )
        replay.exact(
            f"{entry['cell_id']}.shuffled cyclic peer",
            shuffled,
            expected_peer_cell,
        )
    return bases, targets


def check_point_in_subgroup(
    point: Point, curve: dict[str, Any], label: str, replay: Replay
) -> None:
    replay.require(point is not None, f"{label}: infinity is not affine")
    replay.require(on_curve(point, curve["p"]), f"{label}: point is off curve")
    replay.exact(
        f"{label}: subgroup",
        ec_mul(curve["n"], point, curve["p"]),
        None,
    )


def reconstruct_factor_base(
    *,
    curve: dict[str, Any],
    arm: str,
    seed: int,
    prefix: bytes,
    size: int = 384,
) -> tuple[list[Point], dict[str, Any]]:
    """Regenerate the ordered base from the frozen counter stream."""

    replay_arm = arm
    if replay_arm not in ARMS:
        raise ValidationFailure(f"unknown factor-base arm {arm!r}")
    if replay_arm == "GLV_ORBIT_CLOSED" and size % 3 != 0:
        raise ValidationFailure("orbit-closed base size must be divisible by three")
    rng = CounterPrng(prefix, prng_domain(curve["curve_id"], arm, seed, "base"))
    p = curve["p"]
    n = curve["n"]
    generator_raw = curve["generator"]
    generator = (generator_raw["x"], generator_raw["y"])
    beta = curve["beta"]
    operation_counts = zero_operation_counts()
    points: list[Point] = []
    used_x: set[int] = set()
    counters = {
        "draws": 0,
        "rejected_zero_scalar": 0,
        "rejected_x_collision": 0,
        "rejected_orbit_collision": 0,
        "accepted_plain_orbit_relation": 0,
    }
    while len(points) < size:
        counters["draws"] += 1
        scalar = rng.randbelow(n - 1) + 1
        point = counted_ec_mul(scalar, generator, p, operation_counts)
        if point is None:
            raise ValidationFailure("nonzero subgroup scalar produced infinity")
        if arm == "GLV_ORBIT_CLOSED":
            orbit = [
                point,
                (beta * point[0] % p, point[1]),
                (beta * beta * point[0] % p, point[1]),
            ]
            orbit_x = [candidate[0] for candidate in orbit]
            if len(set(orbit_x)) != 3:
                counters["rejected_orbit_collision"] += 1
                continue
            if any(x in used_x for x in orbit_x):
                counters["rejected_x_collision"] += 1
                continue
            points.extend(orbit)
            used_x.update(orbit_x)
        else:
            if point[0] in used_x:
                counters["rejected_x_collision"] += 1
                continue
            if (
                point[0] * beta % p in used_x
                or point[0] * beta * beta % p in used_x
            ):
                counters["accepted_plain_orbit_relation"] += 1
            points.append(point)
            used_x.add(point[0])
    counters["prng_words"] = rng.counter
    counters["prng_rejected_blocks"] = rng.rejected_blocks
    counters["operation_counts"] = operation_counts
    return points, counters


def reconstruct_target_point(
    *, curve: dict[str, Any], seed: int, prefix: bytes
) -> Point:
    rng = CounterPrng(
        prefix,
        prng_domain(curve["curve_id"], "PAIRED_TARGET", seed, "target"),
    )
    scalar = rng.randbelow(curve["n"] - 1) + 1
    generator_raw = curve["generator"]
    generator = (generator_raw["x"], generator_raw["y"])
    target = ec_mul(scalar, generator, curve["p"])
    if target is None:
        raise ValidationFailure("nonzero target scalar produced identity")
    return target


def replay_leaf_trial(
    rng: CounterPrng,
    factor_base: Sequence[Point],
    target: Point,
    p: int,
) -> tuple[list[int], list[int], Point]:
    indices = [rng.randbelow(len(factor_base)) for _ in range(15)]
    signs = [1 if rng.randbelow(2) else -1 for _ in range(15)]
    points = [
        factor_base[index] if sign == 1 else ec_neg(factor_base[index], p)
        for index, sign in zip(indices, signs)
    ]
    residual = ec_sub(target, ec_sum(points, p), p)
    return indices, signs, residual


def deterministic_permutation(
    *,
    curve_id: str,
    arm: str,
    seed: int,
    trial_index: int,
    permutation_index: int,
    prefix: bytes,
) -> list[int]:
    rng = CounterPrng(
        prefix,
        prng_domain(
            curve_id,
            arm,
            seed,
            f"permutation/{trial_index}/{permutation_index}",
        ),
    )
    order = list(range(16))
    for cursor in range(15, 0, -1):
        other = rng.randbelow(cursor + 1)
        order[cursor], order[other] = order[other], order[cursor]
    return order


def base_commitment(
    curve_id: str,
    arm: str,
    seed: int,
    points: Sequence[Point],
) -> str:
    current_cell = f"{curve_id}--{arm}--S{seed}"
    payload = {
        "arm": arm,
        "cell_id": current_cell,
        "curve_id": curve_id,
        "points": [point_json(point) for point in points],
        "seed": seed,
        "statement": "ordered-factor-base-v1",
    }
    return canonical_sha256(payload)


def target_commitment(target_entry: dict[str, Any]) -> str:
    payload = {
        "base_commitment": target_entry["base_commitment"],
        "cell_id": target_entry["cell_id"],
        "point": target_entry["point"],
        "statement": target_entry["statement"],
    }
    return canonical_sha256(payload)


def check_nonnegative_counts(value: Any, label: str, replay: Replay) -> None:
    replay.require(isinstance(value, dict), f"{label}: expected object")
    replay.require(
        all(
            isinstance(item, int) and not isinstance(item, bool) and item >= 0
            for item in value.values()
        ),
        f"{label}: expected nonnegative integer counts",
    )


def check_base_event(
    event: dict[str, Any],
    *,
    entry: dict[str, Any],
    curve: dict[str, Any],
    points: Sequence[Point],
    build_counts: dict[str, int],
    replay: Replay,
) -> None:
    current_cell = entry["cell_id"]
    replay.exact(
        f"{current_cell}.base event keys",
        set(event),
        {
            "event",
            "cell_id",
            "curve_id",
            "arm",
            "seed",
            "points",
            "commitment",
            "selection_counts",
            "prng_blocks",
            "prng_rejected_blocks",
            "operation_counts",
            "frozen_sequence",
        },
    )
    for key in ("cell_id", "curve_id", "arm", "seed", "frozen_sequence"):
        replay.exact(f"{current_cell}.base.{key}", event.get(key), entry[key])
    replay.exact(f"{current_cell}.base.event", event.get("event"), "base")
    replay.exact(
        f"{current_cell}.base.points",
        event.get("points"),
        [point_json(point) for point in points],
    )
    replay.exact(
        f"{current_cell}.base.commitment",
        event.get("commitment"),
        entry["ordered_base_sha256"],
    )
    selection = {
        key: value
        for key, value in build_counts.items()
        if key not in {
            "prng_words",
            "prng_rejected_blocks",
            "operation_counts",
        }
    }
    replay.exact(
        f"{current_cell}.base.selection_counts",
        event.get("selection_counts"),
        selection,
    )
    replay.exact(
        f"{current_cell}.base.prng_blocks",
        event.get("prng_blocks"),
        build_counts["prng_words"],
    )
    replay.exact(
        f"{current_cell}.base.prng_rejected_blocks",
        event.get("prng_rejected_blocks"),
        build_counts["prng_rejected_blocks"],
    )
    replay.exact(
        f"{current_cell}.base.operation_counts replay",
        event.get("operation_counts"),
        build_counts["operation_counts"],
    )
    for index, point in enumerate(points):
        check_point_in_subgroup(point, curve, f"{current_cell}.base[{index}]", replay)
    x_values = [point[0] for point in points if point is not None]
    replay.exact(f"{current_cell}.base.unique_x", len(set(x_values)), len(points))
    x_set = set(x_values)
    orbit_closed = all(
        curve["beta"] * x % curve["p"] in x_set
        and curve["beta"] * curve["beta"] * x % curve["p"] in x_set
        for x in x_values
    )
    replay.exact(
        f"{current_cell}.base.orbit_closed",
        orbit_closed,
        entry["arm"] == "GLV_ORBIT_CLOSED",
    )


def check_labels(
    claimed: Any, expected: dict[str, Any], label: str, replay: Replay
) -> None:
    replay.require(isinstance(claimed, dict), f"{label}: labels must be object")
    replay.exact(label, claimed, expected)


def replay_accepted(
    record: dict[str, Any],
    *,
    cell: dict[str, Any],
    curve: dict[str, Any],
    factor_base: Sequence[Point],
    target: Point,
    replay: Replay,
    expected_indices: Sequence[int] | None = None,
    expected_signs: Sequence[int] | None = None,
    prng_prefix: bytes = PRNG_PREFIX,
) -> dict[str, Any]:
    cell_id = cell["cell_id"]
    trial_index = record.get("trial_index")
    replay.require(
        isinstance(trial_index, int) and trial_index >= 0,
        f"{cell_id}.accepted: invalid trial index",
    )
    indices = record.get("indices")
    signs = record.get("signs")
    replay.require(
        isinstance(indices, list)
        and len(indices) == 16
        and all(isinstance(index, int) and 0 <= index < len(factor_base)
                for index in indices),
        f"{cell_id}.accepted[{trial_index}]: invalid indices",
    )
    replay.require(
        isinstance(signs, list)
        and len(signs) == 16
        and all(sign in (-1, 1) for sign in signs),
        f"{cell_id}.accepted[{trial_index}]: invalid signs",
    )
    if expected_indices is not None:
        replay.exact(
            f"{cell_id}[{trial_index}]: deterministic index stream",
            indices,
            list(expected_indices),
        )
    if expected_signs is not None:
        replay.exact(
            f"{cell_id}[{trial_index}]: deterministic sign stream",
            signs,
            list(expected_signs),
        )
    p = curve["p"]
    points = [
        factor_base[index] if sign == 1 else ec_neg(factor_base[index], p)
        for index, sign in zip(indices, signs)
    ]
    unsigned_points = [factor_base[index] for index in indices]
    replay.exact(
        f"{cell_id}[{trial_index}]: recorded points",
        record.get("points"),
        [point_json(point) for point in unsigned_points],
    )
    replay.exact(
        f"{cell_id}[{trial_index}]: recorded target",
        record.get("target"),
        point_json(target),
    )
    residual = ec_sub(target, ec_sum(points[:15], p), p)
    replay.require(residual is not None, f"{cell_id}[{trial_index}]: zero residual")
    replay.exact(
        f"{cell_id}[{trial_index}]: residual x membership",
        residual[0],
        factor_base[indices[15]][0],
    )
    replay.exact(
        f"{cell_id}[{trial_index}]: inferred final signed point",
        points[15],
        residual,
    )
    replay.exact(
        f"{cell_id}[{trial_index}]: exact relation",
        ec_sum(points, p),
        target,
    )
    expected_labels = regularity_labels(points, target, p)
    check_labels(
        record.get("labels"),
        expected_labels,
        f"{cell_id}[{trial_index}].labels",
        replay,
    )

    permutations = record.get("permutations")
    replay.require(
        isinstance(permutations, list) and len(permutations) == 16,
        f"{cell_id}[{trial_index}]: expected 16 permutations",
    )
    for permutation_index, item in enumerate(permutations):
        replay.require(
            isinstance(item, dict),
            f"{cell_id}[{trial_index}].permutation[{permutation_index}] object",
        )
        replay.exact(
            f"{cell_id}[{trial_index}].permutation[{permutation_index}].control_index",
            item.get("control_index"),
            permutation_index,
        )
        order = item.get("permutation")
        replay.require(
            isinstance(order, list) and sorted(order) == list(range(16)),
            f"{cell_id}[{trial_index}].permutation[{permutation_index}] invalid order",
        )
        replay.exact(
            f"{cell_id}[{trial_index}].permutation[{permutation_index}] stream",
            order,
            deterministic_permutation(
                curve_id=cell["curve_id"],
                arm=cell["arm"],
                seed=cell["seed"],
                trial_index=trial_index,
                permutation_index=permutation_index,
                prefix=prng_prefix,
            ),
        )
        permuted = [unsigned_points[index] for index in order]
        replay.exact(
            f"{cell_id}[{trial_index}].permutation[{permutation_index}] sum",
            sorted(point[0] for point in permuted if point is not None),
            sorted(point[0] for point in unsigned_points if point is not None),
        )
        check_labels(
            item.get("labels"),
            regularity_labels(permuted, target, p),
            f"{cell_id}[{trial_index}].permutation[{permutation_index}].labels",
            replay,
        )
    return expected_labels


def aggregate_curve_arms(
    cells: Sequence[dict[str, Any]]
) -> dict[tuple[str, str], dict[str, Any]]:
    counts: dict[tuple[str, str], dict[str, int]] = {}
    for cell in cells:
        key = (cell["curve_id"], cell["arm"])
        bucket = counts.setdefault(
            key, {"attempts": 0, "accepted": 0, "affine_regular": 0}
        )
        for field in bucket:
            bucket[field] += cell["counts"][field]
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for key, bucket in counts.items():
        result[key] = {
            **bucket,
            "acceptance_wilson95": rounded_interval(
                bucket["accepted"], bucket["attempts"]
            ),
            "theta_wilson95": rounded_interval(
                bucket["affine_regular"], bucket["accepted"]
            ),
        }
    return result


def decision_metrics(cells: Sequence[dict[str, Any]]) -> dict[str, Any]:
    h_new = DECISION_THRESHOLDS["h_new"]
    per_seed: dict[tuple[str, str, int], dict[str, Any]] = {}
    for cell in cells:
        counts = cell["counts"]
        accepted = counts["accepted"]
        shuffled_accepted = counts["shuffled_accepted"]
        validator_metrics = cell.get(
            "_validator_metrics",
            {
                "permutation_relation_mean_sum": 0.0,
                "permutation_relation_count": accepted,
            },
        )
        per_seed[(cell["curve_id"], cell["arm"], cell["seed"])] = {
            "attempts": counts["attempts"],
            "affine_regular": counts["affine_regular"],
            "accepted": accepted,
            "theta": (
                counts["affine_regular"] / accepted if accepted else None
            ),
            "shuffled_affine_regular": counts["shuffled_affine_regular"],
            "shuffled_accepted": shuffled_accepted,
            "shuffled_theta": (
                counts["shuffled_affine_regular"] / shuffled_accepted
                if shuffled_accepted else None
            ),
            "random_label_true": counts["random_label_true"],
            "random_label_fraction": (
                counts["random_label_true"] / accepted if accepted else None
            ),
            "permutation_relation_mean_sum":
                validator_metrics["permutation_relation_mean_sum"],
            "permutation_relation_count":
                validator_metrics["permutation_relation_count"],
            "permutation_relation_mean": (
                validator_metrics["permutation_relation_mean_sum"]
                / validator_metrics["permutation_relation_count"]
                if validator_metrics["permutation_relation_count"] else None
            ),
        }

    by_curve_arm: dict[tuple[str, str], dict[str, Any]] = {}
    for curve in EXPECTED_CURVES:
        curve_id = curve["curve_id"]
        for arm in ARMS:
            rows = [
                value for (row_curve, row_arm, _), value in per_seed.items()
                if row_curve == curve_id and row_arm == arm
            ]
            if not rows:
                continue
            accepted = sum(row["accepted"] for row in rows)
            affine = sum(row["affine_regular"] for row in rows)
            shuffled_accepted = sum(row["shuffled_accepted"] for row in rows)
            shuffled_affine = sum(
                row["shuffled_affine_regular"] for row in rows
            )
            permutation_count = sum(
                row["permutation_relation_count"] for row in rows
            )
            permutation_sum = sum(
                row["permutation_relation_mean_sum"] for row in rows
            )
            by_curve_arm[(curve_id, arm)] = {
                "attempts": sum(row["attempts"] for row in rows),
                "accepted": accepted,
                "affine_regular": affine,
                "acceptance_wilson95": rounded_interval(
                    accepted, sum(row["attempts"] for row in rows)
                ),
                "theta": affine / accepted if accepted else None,
                "theta_wilson95": rounded_interval(affine, accepted),
                "shuffled_accepted": shuffled_accepted,
                "shuffled_affine_regular": shuffled_affine,
                "shuffled_theta": (
                    shuffled_affine / shuffled_accepted
                    if shuffled_accepted else None
                ),
                "permutation_relation_mean": (
                    permutation_sum / permutation_count
                    if permutation_count else None
                ),
                "random_label_true": sum(
                    row["random_label_true"] for row in rows
                ),
                "random_label_count": accepted,
                "random_label_fraction": (
                    sum(row["random_label_true"] for row in rows) / accepted
                    if accepted else None
                ),
            }

    by_curve: dict[str, dict[str, Any]] = {}
    seeds = CONFIG_CONTRACT["seeds"]
    for curve in EXPECTED_CURVES:
        curve_id = curve["curve_id"]
        if any((curve_id, arm) not in by_curve_arm for arm in ARMS):
            continue
        orbit = by_curve_arm[(curve_id, "GLV_ORBIT_CLOSED")]
        plain = by_curve_arm[(curve_id, "PLAIN_MATCHED")]
        seed_rows: list[dict[str, Any]] = []
        for seed in seeds:
            orbit_seed = per_seed.get((curve_id, "GLV_ORBIT_CLOSED", seed))
            plain_seed = per_seed.get((curve_id, "PLAIN_MATCHED", seed))
            if orbit_seed is None or plain_seed is None:
                continue
            seed_rows.append(
                {
                    "seed": seed,
                    "orbit": orbit_seed,
                    "plain": plain_seed,
                    "theta_delta": (
                        orbit_seed["theta"] - plain_seed["theta"]
                        if orbit_seed["theta"] is not None
                        and plain_seed["theta"] is not None
                        else None
                    ),
                    "permutation_delta": (
                        orbit_seed["permutation_relation_mean"]
                        - plain_seed["permutation_relation_mean"]
                        if orbit_seed["permutation_relation_mean"] is not None
                        and plain_seed["permutation_relation_mean"] is not None
                        else None
                    ),
                }
            )
        theta_delta = (
            orbit["theta"] - plain["theta"]
            if orbit["theta"] is not None and plain["theta"] is not None
            else None
        )
        nonoverlap = (
            orbit["theta_wilson95"][0] > plain["theta_wilson95"][1]
            or plain["theta_wilson95"][0] > orbit["theta_wilson95"][1]
        )
        by_curve[curve_id] = {
            "orbit": orbit,
            "plain": plain,
            "pooled_theta_delta": theta_delta,
            "pooled_theta_intervals_nonoverlap": nonoverlap,
            "paired_seeds": seed_rows,
            "positive_theta_pairs": sum(
                row["theta_delta"] is not None and row["theta_delta"] > 0
                for row in seed_rows
            ),
            "negative_theta_pairs": sum(
                row["theta_delta"] is not None and row["theta_delta"] < 0
                for row in seed_rows
            ),
            "pooled_shuffled_delta": (
                orbit["shuffled_theta"] - plain["shuffled_theta"]
                if orbit["shuffled_theta"] is not None
                and plain["shuffled_theta"] is not None
                else None
            ),
            "pooled_permutation_delta": (
                orbit["permutation_relation_mean"]
                - plain["permutation_relation_mean"]
                if orbit["permutation_relation_mean"] is not None
                and plain["permutation_relation_mean"] is not None
                else None
            ),
            "positive_permutation_pairs": sum(
                row["permutation_delta"] is not None
                and row["permutation_delta"] > 0
                for row in seed_rows
            ),
            "random_label_pooled_delta": (
                abs(
                    orbit["random_label_fraction"]
                    - plain["random_label_fraction"]
                )
                if orbit["random_label_fraction"] is not None
                and plain["random_label_fraction"] is not None
                else None
            ),
        }

    primary_promotion_gates_pass = promotion_gates_pass(
        aggregate_curve_arms(cells)
    )
    qualifying_sizes: list[str] = []
    for curve in EXPECTED_CURVES:
        curve_id = curve["curve_id"]
        if curve_id not in by_curve:
            continue
        value = by_curve[curve_id]
        random_arm_ok = all(
            value[arm]["random_label_fraction"] is not None
            and h_new["random_label_rate_interval"][0]
            <= value[arm]["random_label_fraction"]
            <= h_new["random_label_rate_interval"][1]
            for arm in ("orbit", "plain")
        )
        controls_ok = (
            value["orbit"]["shuffled_accepted"]
            >= h_new["shuffled_minimum_accepted_per_arm_size"]
            and value["plain"]["shuffled_accepted"]
            >= h_new["shuffled_minimum_accepted_per_arm_size"]
            and value["pooled_shuffled_delta"] is not None
            and value["pooled_shuffled_delta"]
            >= h_new["shuffled_pooled_orbit_minus_plain_minimum"]
            and value["pooled_permutation_delta"] is not None
            and value["pooled_permutation_delta"]
            >= h_new["permutation_mean_orbit_minus_plain_minimum"]
            and value["positive_permutation_pairs"]
            >= h_new["permutation_minimum_positive_paired_seeds_per_size"]
            and random_arm_ok
            and value["random_label_pooled_delta"] is not None
            and value["random_label_pooled_delta"]
            < h_new["random_label_maximum_absolute_arm_delta"]
        )
        if (
            primary_promotion_gates_pass
            and
            value["pooled_theta_delta"] is not None
            and value["pooled_theta_delta"]
            >= h_new["primary_pooled_orbit_minus_plain_minimum"]
            and value["pooled_theta_intervals_nonoverlap"]
            and value["positive_theta_pairs"]
            >= h_new["minimum_positive_paired_seeds_per_size"]
            and controls_ok
        ):
            qualifying_sizes.append(curve_id)
    serial_per_seed = [
        {
            "curve_id": curve_id,
            "arm": arm,
            "seed": seed,
            **value,
        }
        for (curve_id, arm, seed), value in per_seed.items()
    ]
    serial_per_seed.sort(
        key=lambda row: (
            tuple(curve["curve_id"] for curve in EXPECTED_CURVES).index(
                row["curve_id"]
            ),
            ARMS.index(row["arm"]),
            CONFIG_CONTRACT["seeds"].index(row["seed"]),
        )
    )
    serial_by_curve_arm = [
        {"curve_id": curve_id, "arm": arm, **value}
        for (curve_id, arm), value in by_curve_arm.items()
    ]
    serial_by_curve_arm.sort(
        key=lambda row: (
            tuple(curve["curve_id"] for curve in EXPECTED_CURVES).index(
                row["curve_id"]
            ),
            ARMS.index(row["arm"]),
        )
    )
    return {
        "per_seed": serial_per_seed,
        "by_curve_arm": serial_by_curve_arm,
        "by_curve": by_curve,
        "h_new_qualifying_sizes": qualifying_sizes,
        "primary_promotion_gates_pass": primary_promotion_gates_pass,
        "h_new_signal": (
            len(qualifying_sizes) >= h_new["minimum_qualifying_sizes"]
        ),
        "h_new_status": (
            "POTENTIALLY_NOVEL_NOVELTY_UNVERIFIED"
            if len(qualifying_sizes) >= h_new["minimum_qualifying_sizes"]
            else "NOT_RETAINED"
        ),
    }


def promotion_gates_pass(
    by_key: dict[tuple[str, str], dict[str, Any]]
) -> bool:
    expected_keys = {
        (curve["curve_id"], arm)
        for curve in EXPECTED_CURVES
        for arm in ARMS
    }
    if set(by_key) != expected_keys:
        return False
    if any(
        summary["accepted"]
        < DECISION_THRESHOLDS["minimum_accepted_per_curve_arm"]
        for summary in by_key.values()
    ):
        return False
    large_curve_ids = (
        "E7-P1048783-N1050337",
        "E7-P16777711-N5591281",
    )
    if any(
        by_key[(curve_id, "GLV_ORBIT_CLOSED")]["theta_wilson95"][0]
        < DECISION_THRESHOLDS["promotion_orbit_theta_wilson95_lower"]
        for curve_id in large_curve_ids
    ):
        return False
    m21 = by_key[
        ("E7-P1048783-N1050337", "GLV_ORBIT_CLOSED")
    ]
    m23 = by_key[
        ("E7-P16777711-N5591281", "GLV_ORBIT_CLOSED")
    ]
    theta21 = m21["affine_regular"] / m21["accepted"]
    theta23 = m23["affine_regular"] / m23["accepted"]
    maximum_decline = DECISION_THRESHOLDS[
        "promotion_orbit_maximum_unexplained_m21_to_m23_decline"
    ]
    if (
        theta21 - theta23 > maximum_decline
        and m21["theta_wilson95"][0] > m23["theta_wilson95"][1]
    ):
        return False
    return True


def classify_terminal(cells: Sequence[dict[str, Any]]) -> str:
    by_key = aggregate_curve_arms(cells)
    if by_key and all(summary["accepted"] == 0 for summary in by_key.values()):
        return "KILL_AFFINE_M16_CONTINUATION"
    expected_keys = {
        (curve["curve_id"], arm)
        for curve in EXPECTED_CURVES
        for arm in ARMS
    }
    if set(by_key) != expected_keys or any(
        summary["accepted"]
        < DECISION_THRESHOLDS["minimum_accepted_per_curve_arm"]
        for summary in by_key.values()
    ):
        return "PAUSE_INCONCLUSIVE"

    for curve_id in (
        "E7-P1048783-N1050337",
        "E7-P16777711-N5591281",
    ):
        orbit = by_key[(curve_id, "GLV_ORBIT_CLOSED")]
        if (
            orbit["theta_wilson95"][1]
            < DECISION_THRESHOLDS["kill_orbit_theta_wilson95_upper"]
        ):
            return "KILL_AFFINE_M16_CONTINUATION"
    if not promotion_gates_pass(by_key):
        return "PAUSE_INCONCLUSIVE"

    known = True
    for curve_id in (
        "E7-P1048783-N1050337",
        "E7-P16777711-N5591281",
    ):
        orbit = by_key[(curve_id, "GLV_ORBIT_CLOSED")]
        plain = by_key[(curve_id, "PLAIN_MATCHED")]
        orbit_theta = orbit["affine_regular"] / orbit["accepted"]
        plain_theta = plain["affine_regular"] / plain["accepted"]
        overlap = not (
            orbit["theta_wilson95"][0] > plain["theta_wilson95"][1]
            or plain["theta_wilson95"][0] > orbit["theta_wilson95"][1]
        )
        if (
            plain["theta_wilson95"][0]
            < DECISION_THRESHOLDS[
                "known_local_plain_theta_wilson95_lower"
            ]
            or
            abs(orbit_theta - plain_theta)
            >= DECISION_THRESHOLDS[
                "known_local_maximum_absolute_arm_delta"
            ]
            or (
                DECISION_THRESHOLDS[
                    "known_local_requires_interval_overlap"
                ]
                and not overlap
            )
        ):
            known = False
    if known:
        return "CLASSIFY_AS_KNOWN_LOCAL_SIMPLIFICATION"
    return "PROMOTE_TO_SOLVER_SLOPE_TEST"


def read_canonical_jsonl(path: Path, replay: Replay) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    try:
        with path.open("rb") as handle:
            for line_number, raw_line in enumerate(handle, 1):
                replay.require(raw_line.endswith(b"\n"), f"raw line {line_number}: no LF")
                try:
                    value = json.loads(raw_line)
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise ValidationFailure(
                        f"raw line {line_number}: invalid JSON"
                    ) from exc
                replay.require(
                    isinstance(value, dict),
                    f"raw line {line_number}: event must be object",
                )
                replay.exact(
                    f"raw line {line_number}: canonical encoding",
                    raw_line,
                    canonical_utf8_line(value),
                )
                events.append(value)
    except OSError as exc:
        raise ValidationFailure(f"cannot read raw transcript: {exc}") from exc
    replay.require(bool(events), "raw transcript is empty")
    return events


def check_raw_file_binding(
    raw_path: Path,
    raw_files: Any,
    expected_relative_path: str,
    replay: Replay,
) -> None:
    replay.exact(
        "summary.raw_files",
        raw_files,
        [
            {
                "path": expected_relative_path,
                "sha256": file_sha256(raw_path),
                "bytes": raw_path.stat().st_size,
            }
        ],
    )


def split_raw_events(
    events: Sequence[dict[str, Any]],
    targets: Sequence[dict[str, Any]],
    replay: Replay,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any], dict[str, Any]]:
    replay.exact("raw first event", events[0].get("event"), "run_header")
    cursor = 1
    cells: dict[str, dict[str, Any]] = {}
    for target in targets:
        if cursor < len(events) and events[cursor].get("event") == "run_summary":
            break
        current_cell = target["cell_id"]
        replay.require(cursor + 3 <= len(events), f"{current_cell}: truncated raw block")
        base_event = events[cursor]
        target_event = events[cursor + 1]
        constructed = events[cursor + 2]
        replay.exact(f"{current_cell}.raw base order", base_event.get("event"), "base")
        replay.exact(
            f"{current_cell}.raw target order", target_event.get("event"), "target"
        )
        replay.exact(
            f"{current_cell}.raw control order",
            constructed.get("event"),
            "constructed_control",
        )
        for label, event in (
            ("base", base_event),
            ("target", target_event),
            ("constructed", constructed),
        ):
            replay.exact(
                f"{current_cell}.{label}.cell_id",
                event.get("cell_id"),
                current_cell,
            )
        cursor += 3
        accepted: dict[int, dict[str, Any]] = {}
        shuffled: dict[int, dict[str, Any]] = {}
        last_order_key = (-1, -1)
        while cursor < len(events) and events[cursor].get("event") in {
            "accepted",
            "shuffled_accepted",
        }:
            event = events[cursor]
            replay.exact(
                f"{current_cell}.trial event cell",
                event.get("cell_id"),
                current_cell,
            )
            trial = event.get("trial_index")
            replay.require(
                isinstance(trial, int) and trial >= 0,
                f"{current_cell}: invalid trial index",
            )
            type_order = 0 if event["event"] == "accepted" else 1
            order_key = (trial, type_order)
            replay.require(
                order_key > last_order_key,
                f"{current_cell}: trial events out of order or duplicated",
            )
            last_order_key = order_key
            destination = accepted if type_order == 0 else shuffled
            replay.require(trial not in destination, f"{current_cell}: duplicate trial")
            destination[trial] = event
            cursor += 1
        replay.require(cursor < len(events), f"{current_cell}: missing cell_summary")
        summary = events[cursor]
        replay.exact(
            f"{current_cell}.raw summary order",
            summary.get("event"),
            "cell_summary",
        )
        replay.exact(
            f"{current_cell}.raw summary cell",
            summary.get("cell_id"),
            current_cell,
        )
        cursor += 1
        cells[current_cell] = {
            "base": base_event,
            "target": target_event,
            "constructed": constructed,
            "accepted": accepted,
            "shuffled": shuffled,
            "summary": summary,
        }
        if summary.get("cell_complete") is False:
            break
    replay.require(cursor < len(events), "raw transcript missing run_summary")
    run_summary = events[cursor]
    replay.exact("raw final event", run_summary.get("event"), "run_summary")
    replay.exact("raw event exhaustion", cursor + 1, len(events))
    return cells, events[0], run_summary


def reconstruct_constructed_control(
    *,
    curve: dict[str, Any],
    arm: str,
    seed: int,
    factor_base: Sequence[Point],
) -> dict[str, Any]:
    attempt = 0
    while True:
        role = f"constructed-control/{attempt}"
        rng = CounterPrng(
            PRNG_PREFIX,
            prng_domain(curve["curve_id"], arm, seed, role),
        )
        indices = [rng.randbelow(len(factor_base)) for _ in range(16)]
        signs = [1 if rng.randbelow(2) == 1 else -1 for _ in range(16)]
        points = [factor_base[index] for index in indices]
        signed = [
            point if sign == 1 else ec_neg(point, curve["p"])
            for point, sign in zip(points, signs)
        ]
        target = ec_sum(signed, curve["p"])
        if target is not None:
            return {
                "event": "constructed_control",
                "cell_id": f"{curve['curve_id']}--{arm}--S{seed}",
                "attempt": attempt,
                "role": role,
                "indices": indices,
                "signs": signs,
                "points": [point_json(point) for point in points],
                "constructed_target": point_json(target),
                "replay_pass": True,
                "included_in_primary": False,
            }
        attempt += 1


OPERATION_COUNT_KEYS = {
    "curve_additions",
    "curve_doublings",
    "identity_shortcuts",
    "field_inversions",
    "scalar_multiplication_bits",
}


def check_operation_counts(value: Any, label: str, replay: Replay) -> None:
    replay.require(isinstance(value, dict), f"{label}: expected object")
    replay.exact(f"{label}.keys", set(value), OPERATION_COUNT_KEYS)
    check_nonnegative_counts(value, label, replay)


def sum_operation_counts(values: Iterable[dict[str, int]]) -> dict[str, int]:
    total = zero_operation_counts()
    for value in values:
        for key in total:
            total[key] += value[key]
    return total


def check_resource_usage(
    value: Any,
    *,
    budget: dict[str, Any],
    resource_reason: str | None,
    replay: Replay,
) -> None:
    replay.require(isinstance(value, dict), "resource usage must be an object")
    replay.exact(
        "resource usage keys",
        set(value),
        {"cpu_hours", "wall_hours", "peak_rss_gib"},
    )
    for key, measurement in value.items():
        replay.require(
            isinstance(measurement, (int, float))
            and not isinstance(measurement, bool)
            and math.isfinite(measurement)
            and measurement >= 0,
            f"resource_usage.{key}: expected finite nonnegative number",
        )
    cap_by_measurement = {
        "cpu_hours": budget["max_cpu_hours"],
        "wall_hours": budget["max_wall_hours"],
        "peak_rss_gib": budget["max_peak_rss_gib"],
    }
    if resource_reason is None:
        for key, cap in cap_by_measurement.items():
            replay.require(
                value[key] <= cap,
                f"complete run exceeds {key} cap",
            )
        return
    reason_to_measurement = {
        "maximum CPU-hour budget reached": "cpu_hours",
        "maximum peak-RSS budget reached": "peak_rss_gib",
        "maximum wall-hour budget reached": "wall_hours",
        "maximum primary-trial budget reached": None,
    }
    replay.require(
        resource_reason in reason_to_measurement,
        "unknown resource-exhaustion reason",
    )
    measurement = reason_to_measurement[resource_reason]
    if measurement is not None:
        replay.require(
            value[measurement] > cap_by_measurement[measurement],
            f"resource reason does not match {measurement}",
        )


def replay_shuffled_accepted(
    event: dict[str, Any],
    *,
    current_cell: str,
    source_target_cell_id: str,
    trial_index: int,
    indices: Sequence[int],
    signs: Sequence[int],
    factor_base: Sequence[Point],
    target: Point,
    curve: dict[str, Any],
    replay: Replay,
) -> dict[str, Any]:
    replay.exact(
        f"{current_cell}.shuffled[{trial_index}].keys",
        set(event),
        {
            "event",
            "cell_id",
            "source_target_cell_id",
            "trial_index",
            "indices",
            "signs",
            "points",
            "target",
            "labels",
        },
    )
    replay.exact(f"{current_cell}.shuffled.event", event["event"],
                 "shuffled_accepted")
    replay.exact(f"{current_cell}.shuffled.cell", event["cell_id"], current_cell)
    replay.exact(
        f"{current_cell}.shuffled.source target",
        event["source_target_cell_id"],
        source_target_cell_id,
    )
    replay.exact(
        f"{current_cell}.shuffled.trial", event["trial_index"], trial_index
    )
    replay.exact(f"{current_cell}.shuffled.indices", event["indices"], list(indices))
    replay.exact(f"{current_cell}.shuffled.signs", event["signs"], list(signs))
    points = [factor_base[index] for index in indices]
    replay.exact(
        f"{current_cell}.shuffled.points",
        event["points"],
        [point_json(point) for point in points],
    )
    replay.exact(
        f"{current_cell}.shuffled.target", event["target"], point_json(target)
    )
    signed = [
        point if sign == 1 else ec_neg(point, curve["p"])
        for point, sign in zip(points, signs)
    ]
    replay.exact(
        f"{current_cell}.shuffled.relation",
        ec_sum(signed, curve["p"]),
        target,
    )
    labels = regularity_labels(points, target, curve["p"])
    check_labels(
        event["labels"],
        labels,
        f"{current_cell}.shuffled[{trial_index}].labels",
        replay,
    )
    return labels


def validate_cell_transcript(
    *,
    bundle: dict[str, Any],
    target_entry: dict[str, Any],
    shuffled_entry: dict[str, Any],
    base_entry: dict[str, Any],
    factor_base: Sequence[Point],
    curve: dict[str, Any],
    config: dict[str, Any],
    replay: Replay,
) -> dict[str, Any]:
    current_cell = target_entry["cell_id"]
    _, build_counts = reconstruct_factor_base(
        curve=curve,
        arm=target_entry["arm"],
        seed=target_entry["seed"],
        prefix=PRNG_PREFIX,
        size=config["factor_base_size"],
    )
    check_base_event(
        bundle["base"],
        entry=base_entry,
        curve=curve,
        points=factor_base,
        build_counts=build_counts,
        replay=replay,
    )

    target_event = bundle["target"]
    replay.exact(
        f"{current_cell}.target event keys",
        set(target_event),
        {"event", "target_base_x_collision"} | set(target_entry),
    )
    replay.exact(f"{current_cell}.target event type", target_event["event"], "target")
    for key, expected in target_entry.items():
        replay.exact(f"{current_cell}.target.{key}", target_event[key], expected)
    target = parse_point(target_entry["point"], f"{current_cell}.target", replay)
    shuffled_target = parse_point(
        shuffled_entry["point"], f"{current_cell}.shuffled_target", replay
    )
    replay.require(target is not None and shuffled_target is not None,
                   f"{current_cell}: affine targets required")
    x_to_index = {
        point[0]: index for index, point in enumerate(factor_base)
        if point is not None
    }
    replay.exact(
        f"{current_cell}.target base collision",
        target_event["target_base_x_collision"],
        target[0] in x_to_index,
    )
    replay.exact(
        f"{current_cell}.constructed control",
        bundle["constructed"],
        reconstruct_constructed_control(
            curve=curve,
            arm=target_entry["arm"],
            seed=target_entry["seed"],
            factor_base=factor_base,
        ),
    )

    leaf_stream = CounterPrng(
        PRNG_PREFIX,
        prng_domain(
            curve["curve_id"],
            target_entry["arm"],
            target_entry["seed"],
            "leaves",
        ),
    )
    random_label_stream = CounterPrng(
        PRNG_PREFIX,
        prng_domain(
            curve["curve_id"],
            target_entry["arm"],
            target_entry["seed"],
            "random-label",
        ),
    )
    planned_attempts = config["trials_per_seed"][curve["curve_id"]]
    summary = bundle["summary"]
    claimed_counts = summary.get("counts")
    replay.require(
        isinstance(claimed_counts, dict)
        and isinstance(claimed_counts.get("attempts"), int)
        and not isinstance(claimed_counts.get("attempts"), bool),
        f"{current_cell}: summary has no integer attempt count",
    )
    attempts = claimed_counts["attempts"]
    replay.require(
        0 <= attempts <= planned_attempts,
        f"{current_cell}: actual attempts outside frozen cap",
    )
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
    endpoint_failures = {"base": 0, "final": 0}
    prefix_failures = [0] * 6
    suffix_failures = [0] * 6
    permutation_relation_mean_sum = 0.0
    accepted_events = bundle["accepted"]
    shuffled_events = bundle["shuffled"]
    for trial_index in range(attempts):
        indices15, signs15, residual = replay_leaf_trial(
            leaf_stream, factor_base, target, curve["p"]
        )
        counts["attempts"] += 1
        if residual is None:
            counts["residual_identity"] += 1
            replay.require(
                trial_index not in accepted_events,
                f"{current_cell}[{trial_index}]: false accepted identity residual",
            )
        elif residual[0] not in x_to_index:
            counts["residual_not_in_base"] += 1
            replay.require(
                trial_index not in accepted_events,
                f"{current_cell}[{trial_index}]: false accepted nonmember residual",
            )
        else:
            replay.require(
                trial_index in accepted_events,
                f"{current_cell}[{trial_index}]: missing accepted relation",
            )
            final_index = x_to_index[residual[0]]
            final_point = factor_base[final_index]
            final_sign = 1 if residual == final_point else -1
            indices = indices15 + [final_index]
            signs = signs15 + [final_sign]
            event = accepted_events[trial_index]
            replay.exact(
                f"{current_cell}[{trial_index}].accepted keys",
                set(event),
                {
                    "event",
                    "cell_id",
                    "trial_index",
                    "indices",
                    "signs",
                    "points",
                    "target",
                    "labels",
                    "permutations",
                    "random_label",
                    "repeated_index_count",
                    "repeated_coordinate_count",
                    "target_coordinate_collision_count",
                    "operation_counts",
                },
            )
            replay.exact(f"{current_cell}[{trial_index}].event",
                         event["event"], "accepted")
            replay.exact(f"{current_cell}[{trial_index}].cell",
                         event["cell_id"], current_cell)
            labels = replay_accepted(
                event,
                cell=target_entry,
                curve=curve,
                factor_base=factor_base,
                target=target,
                replay=replay,
                expected_indices=indices,
                expected_signs=signs,
                prng_prefix=PRNG_PREFIX,
            )
            permutation_relation_mean_sum += sum(
                int(control["labels"]["affine_regular"])
                for control in event["permutations"]
            ) / len(event["permutations"])
            random_label = random_label_stream.randbelow(2) == 1
            replay.exact(
                f"{current_cell}[{trial_index}].random_label",
                event["random_label"],
                random_label,
            )
            expected_repeated_index = 16 - len(set(indices))
            expected_repeated_coordinate = 16 - len(
                {factor_base[index][0] for index in indices}
            )
            expected_target_collision = sum(
                factor_base[index][0] == target[0] for index in indices
            )
            replay.exact(
                f"{current_cell}[{trial_index}].repeated_index_count",
                event["repeated_index_count"],
                expected_repeated_index,
            )
            replay.exact(
                f"{current_cell}[{trial_index}].repeated_coordinate_count",
                event["repeated_coordinate_count"],
                expected_repeated_coordinate,
            )
            replay.exact(
                f"{current_cell}[{trial_index}].target_coordinate_collision_count",
                event["target_coordinate_collision_count"],
                expected_target_collision,
            )
            check_operation_counts(
                event["operation_counts"],
                f"{current_cell}[{trial_index}].operation_counts",
                replay,
            )
            counts["accepted"] += 1
            counts["affine_regular"] += int(labels["affine_regular"])
            counts["balanced_regular"] += int(labels["balanced_regular"])
            counts["random_label_true"] += int(random_label)
            counts["repeated_index_total"] += expected_repeated_index
            counts["repeated_coordinate_total"] += expected_repeated_coordinate
            counts["target_coordinate_collision_total"] += expected_target_collision
            endpoint_failures["base"] += int(
                not labels["base_endpoint_nonzero"]
            )
            endpoint_failures["final"] += int(
                not labels["final_endpoint_nonzero"]
            )
            for index in range(6):
                prefix_failures[index] += int(not labels["prefix_nonzero"][index])
                suffix_failures[index] += int(not labels["suffix_nonzero"][index])

        signed15 = [
            factor_base[index] if sign == 1
            else ec_neg(factor_base[index], curve["p"])
            for index, sign in zip(indices15, signs15)
        ]
        control_residual = ec_sub(
            shuffled_target, ec_sum(signed15, curve["p"]), curve["p"]
        )
        if control_residual is not None and control_residual[0] in x_to_index:
            replay.require(
                trial_index in shuffled_events,
                f"{current_cell}[{trial_index}]: missing shuffled acceptance",
            )
            final_index = x_to_index[control_residual[0]]
            final_point = factor_base[final_index]
            final_sign = 1 if control_residual == final_point else -1
            control_indices = indices15 + [final_index]
            control_signs = signs15 + [final_sign]
            labels = replay_shuffled_accepted(
                shuffled_events[trial_index],
                current_cell=current_cell,
                source_target_cell_id=target_entry["shuffled_target_cell_id"],
                trial_index=trial_index,
                indices=control_indices,
                signs=control_signs,
                factor_base=factor_base,
                target=shuffled_target,
                curve=curve,
                replay=replay,
            )
            counts["shuffled_accepted"] += 1
            counts["shuffled_affine_regular"] += int(labels["affine_regular"])
        else:
            replay.require(
                trial_index not in shuffled_events,
                f"{current_cell}[{trial_index}]: false shuffled acceptance",
            )

    replay.exact(
        f"{current_cell}.accepted event exhaustion",
        set(accepted_events),
        {
            trial
            for trial in accepted_events
            if 0 <= trial < attempts
        },
    )
    replay.exact(
        f"{current_cell}.shuffled event exhaustion",
        set(shuffled_events),
        {
            trial
            for trial in shuffled_events
            if 0 <= trial < attempts
        },
    )
    replay.exact(
        f"{current_cell}.summary keys",
        set(summary),
        {
            "event",
            "cell_id",
            "curve_id",
            "m",
            "arm",
            "seed",
            "planned_attempts",
            "cell_complete",
            "counts",
            "endpoint_failures",
            "prefix_failures",
            "suffix_failures",
            "leaf_prng_blocks",
            "leaf_prng_rejected_blocks",
            "operation_counts",
        },
    )
    for key, expected in {
        "event": "cell_summary",
        "cell_id": current_cell,
        "curve_id": curve["curve_id"],
        "m": curve["m"],
        "arm": target_entry["arm"],
        "seed": target_entry["seed"],
        "planned_attempts": planned_attempts,
        "cell_complete": attempts == planned_attempts,
        "counts": counts,
        "endpoint_failures": endpoint_failures,
        "prefix_failures": prefix_failures,
        "suffix_failures": suffix_failures,
        "leaf_prng_blocks": leaf_stream.counter,
        "leaf_prng_rejected_blocks": leaf_stream.rejected_blocks,
    }.items():
        replay.exact(f"{current_cell}.summary.{key}", summary[key], expected)
    check_operation_counts(
        summary["operation_counts"],
        f"{current_cell}.summary.operation_counts",
        replay,
    )
    validated_summary = dict(summary)
    validated_summary["_validator_metrics"] = {
        "permutation_relation_mean_sum": permutation_relation_mean_sum,
        "permutation_relation_count": counts["accepted"],
    }
    return validated_summary


def check_upstream_bindings(bindings: Any, replay: Replay) -> None:
    replay.exact("artifact.upstream_bindings", bindings, UPSTREAM_BINDINGS)
    for relative, expected_digest in UPSTREAM_BINDINGS.items():
        path = REPO_ROOT / relative
        replay.require(path.is_file(), f"missing upstream binding {relative}")
        replay.exact(f"upstream {relative}", file_sha256(path), expected_digest)


def check_upstream_files(replay: Replay) -> None:
    for relative, expected_digest in UPSTREAM_BINDINGS.items():
        path = REPO_ROOT / relative
        replay.require(path.is_file(), f"missing upstream binding {relative}")
        replay.exact(f"upstream {relative}", file_sha256(path), expected_digest)


def check_no_outcomes(config: dict[str, Any], replay: Replay) -> None:
    output = config["output_contract"]
    forbidden = [
        path for path in (
            ARTIFACT_PATH,
            SIDECAR_PATH,
            HERE / "RESULTS.md",
            HERE / output["manifest"],
            HERE / output["summary"],
            HERE / output["raw_jsonl"],
        ) if path.exists()
    ]
    replay.require(
        not forbidden,
        "pre-execution branch contains outcome files: "
        + ", ".join(str(path.relative_to(HERE)) for path in forbidden),
    )


def readiness_check(
    *,
    curve_table_path: Path = CURVE_TABLE_PATH,
    config_path: Path = CONFIG_PATH,
) -> dict[str, Any]:
    """Validate frozen inputs and prove that no outcome was generated."""

    if not curve_table_path.is_file() or not config_path.is_file():
        missing = [
            str(path)
            for path in (curve_table_path, config_path)
            if not path.is_file()
        ]
        raise ValidationInconclusive(
            "missing readiness inputs: " + ", ".join(missing)
        )
    replay = Replay()
    curves = check_curve_table(load_json(curve_table_path), replay)
    config = load_json(config_path)
    preregistration_path = HERE / "PREREGISTRATION.md"
    bases, targets = check_config(
        config,
        curves,
        replay,
        curve_table_path=curve_table_path,
        preregistration_path=preregistration_path,
    )
    replay.exact("readiness base cell count", len(bases), 30)
    replay.exact("readiness target cell count", len(targets), 30)
    check_upstream_files(replay)

    check_no_outcomes(config, replay)
    substrate = load_json(REPO_ROOT / config["authorization_contract"]["path"])
    authorization = substrate.get(
        config["authorization_contract"]["singleton_key"]
    )
    if authorization is not None:
        replay.require(
            isinstance(authorization, dict),
            "authorization singleton must be an object",
        )
        replay.require(
            authorization.get("status") != "approved",
            "readiness-only branch already has approved execution",
        )
    return {"validation_status": "READINESS_PASS", "checks": replay.checks}


def check_manifest(
    manifest: Any,
    *,
    curve_table_path: Path,
    config_path: Path,
    replay: Replay,
) -> None:
    replay.require(isinstance(manifest, dict), "run manifest: expected object")
    replay.exact(
        "manifest keys",
        set(manifest),
        {
            "schema_version",
            "run_id",
            "hypothesis_id",
            "authorization_id",
            "authorization_source_commit",
            "bindings",
            "chronology",
        },
    )
    replay.exact(
        "manifest.schema_version",
        manifest["schema_version"],
        "keyai-m16-fixed-target-producer-v1",
    )
    replay.exact("manifest.hypothesis_id", manifest["hypothesis_id"], HYPOTHESIS_ID)
    replay.require(
        isinstance(manifest["run_id"], str) and bool(manifest["run_id"]),
        "manifest.run_id must be nonempty",
    )
    replay.exact(
        "manifest authorization id",
        manifest["authorization_id"],
        manifest["run_id"],
    )
    replay.require(
        isinstance(manifest["authorization_source_commit"], str)
        and re.fullmatch(
            r"[0-9a-f]{40}", manifest["authorization_source_commit"]
        ) is not None,
        "manifest source commit must be lowercase SHA-1",
    )
    replay.exact(
        "manifest.bindings",
        manifest["bindings"],
        {
            "preregistration_sha256": file_sha256(HERE / "PREREGISTRATION.md"),
            "curve_table_sha256": file_sha256(curve_table_path),
            "experiment_config_sha256": file_sha256(config_path),
            "run_py_sha256": file_sha256(HERE / "run.py"),
            "validate_py_sha256": file_sha256(Path(__file__).resolve()),
        },
    )
    replay.exact(
        "manifest chronology sequences",
        {
            key: manifest["chronology"].get(key)
            for key in (
                "base_manifest_frozen_sequence",
                "targets_committed_sequence",
                "leaves_started_sequence",
            )
        },
        {
            "base_manifest_frozen_sequence": 1,
            "targets_committed_sequence": 2,
            "leaves_started_sequence": 3,
        },
    )
    parse_utc_timestamp(
        manifest["chronology"].get("run_started_utc"),
        "manifest.run_started_utc",
        replay,
    )


def git_file_bytes(commit: str, relative_path: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "show", f"{commit}:{relative_path}"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        raise ValidationFailure(
            f"cannot read {relative_path} at {commit}"
        ) from exc
    return result.stdout


def check_committed_bytes(
    path: Path, committed: bytes, label: str, replay: Replay
) -> None:
    replay.exact(
        label,
        hashlib.sha256(committed).hexdigest(),
        file_sha256(path),
    )


def check_approved_authorization(
    *,
    config: dict[str, Any],
    config_path: Path,
    curve_table_path: Path,
    replay: Replay,
    substrate_path: Path | None = None,
    check_git_history: bool = True,
    authorization_not_after: datetime | None = None,
) -> dict[str, Any]:
    """Independently validate the immutable pre-execution singleton."""

    if substrate_path is None:
        substrate_path = REPO_ROOT / config["authorization_contract"]["path"]
    substrate = load_json(substrate_path)
    replay.require(isinstance(substrate, dict), "authorization substrate object")
    authorization = substrate.get(
        config["authorization_contract"]["singleton_key"]
    )
    replay.require(
        isinstance(authorization, dict),
        "canonical approved authorization is absent",
    )
    replay.exact(
        "authorization field set",
        set(authorization),
        {
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
        },
    )
    for key, expected in {
        "status": "approved",
        "hypothesis_id": HYPOTHESIS_ID,
        "task_id": TASK_ID,
        "route_id": ROUTE_ID,
        "cell_id": RESEARCH_CELL_ID,
        "promotion_authorized": False,
        "resource_budget": config["resource_budget"],
        "scope": {
            "kind": "synthetic_toy_only",
            "curve_family": "E_7",
            "curve_ids": config["curve_ids"],
            "max_field_bits": 25,
            "real_world_targets_forbidden": True,
            "secp256k1_targets_forbidden": True,
        },
    }.items():
        replay.exact(f"authorization.{key}", authorization.get(key), expected)
    replay.require(
        isinstance(authorization.get("authorization_id"), str)
        and bool(authorization["authorization_id"]),
        "authorization.authorization_id must be a nonempty string",
    )
    replay.require(
        isinstance(authorization.get("source_commit"), str)
        and re.fullmatch(r"[0-9a-f]{40}", authorization["source_commit"])
        is not None,
        "authorization.source_commit must be an exact lowercase Git SHA",
    )
    authorized = parse_utc_timestamp(
        authorization.get("authorized_utc"), "authorization.authorized_utc", replay
    )
    if authorization_not_after is not None:
        replay.require(
            authorized <= authorization_not_after,
            "authorization timestamp is in the future",
        )
    bound_paths = {
        "preregistration": HERE / "PREREGISTRATION.md",
        "curve_table": curve_table_path,
        "experiment_config": config_path,
        "run_py": HERE / "run.py",
        "validate_py": Path(__file__).resolve(),
    }
    bindings = authorization.get("sha256_bindings")
    replay.require(
        isinstance(bindings, dict),
        "authorization.sha256_bindings must be an object",
    )
    replay.exact(
        "authorization sha256 binding keys",
        set(bindings),
        set(bound_paths),
    )
    for key, path in bound_paths.items():
        replay.exact(
            f"authorization.sha256_bindings.{key}",
            bindings.get(key),
            file_sha256(path),
        )
    if not check_git_history:
        return authorization
    source_commit = authorization["source_commit"]
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        ancestry = subprocess.run(
            ["git", "merge-base", "--is-ancestor", source_commit, head],
            cwd=REPO_ROOT,
            check=False,
        ).returncode
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValidationFailure("cannot inspect authorization ancestry") from exc
    replay.require(source_commit != head, "authorization source is not pre-approval")
    replay.exact("authorization source ancestry", ancestry, 0)
    try:
        substrate_relative = substrate_path.relative_to(REPO_ROOT).as_posix()
    except ValueError as exc:
        raise ValidationFailure(
            "canonical authorization substrate is outside the repository"
        ) from exc
    check_committed_bytes(
        substrate_path,
        git_file_bytes(head, substrate_relative),
        "canonical authorization substrate committed at HEAD",
        replay,
    )
    for path in bound_paths.values():
        relative = path.relative_to(REPO_ROOT).as_posix()
        replay.exact(
            f"authorization source binding {relative}",
            hashlib.sha256(git_file_bytes(source_commit, relative)).hexdigest(),
            file_sha256(path),
        )
    source_substrate = json.loads(git_file_bytes(source_commit, substrate_relative))
    replay.require(
        isinstance(source_substrate, dict),
        "readiness-source authorization substrate must be an object",
    )
    source_authorization = source_substrate.get(
        config["authorization_contract"]["singleton_key"]
    )
    replay.require(
        source_authorization is None or isinstance(source_authorization, dict),
        "readiness-source authorization singleton is malformed",
    )
    replay.require(
        not (
            isinstance(source_authorization, dict)
            and source_authorization.get("status") == "approved"
        ),
        "readiness source already contained approved authorization",
    )
    return authorization


def check_canonical_authorization(
    *,
    manifest: dict[str, Any],
    config: dict[str, Any],
    config_path: Path,
    curve_table_path: Path,
    replay: Replay,
    substrate_path: Path | None = None,
    check_git_history: bool = True,
) -> None:
    authorization = check_approved_authorization(
        config=config,
        config_path=config_path,
        curve_table_path=curve_table_path,
        replay=replay,
        substrate_path=substrate_path,
        check_git_history=check_git_history,
    )
    replay.exact(
        "authorization/manifest authorization id",
        manifest["authorization_id"],
        authorization["authorization_id"],
    )
    replay.exact(
        "authorization/manifest source commit",
        manifest["authorization_source_commit"],
        authorization["source_commit"],
    )
    replay.exact(
        "authorization/manifest run id",
        manifest["run_id"],
        authorization["authorization_id"],
    )
    authorized = parse_utc_timestamp(
        authorization["authorized_utc"],
        "authorization.authorized_utc",
        replay,
    )
    started = parse_utc_timestamp(
        manifest["chronology"].get("run_started_utc"),
        "authorization run_started_utc",
        replay,
    )
    replay.require(authorized <= started, "run began before authorization")
    replay.exact(
        "authorization manifest bindings",
        manifest["bindings"],
        {
            "preregistration_sha256":
                authorization["sha256_bindings"]["preregistration"],
            "curve_table_sha256":
                authorization["sha256_bindings"]["curve_table"],
            "experiment_config_sha256":
                authorization["sha256_bindings"]["experiment_config"],
            "run_py_sha256": authorization["sha256_bindings"]["run_py"],
            "validate_py_sha256": authorization["sha256_bindings"]["validate_py"],
        },
    )


def authorization_check(
    *,
    curve_table_path: Path = CURVE_TABLE_PATH,
    config_path: Path = CONFIG_PATH,
) -> dict[str, Any]:
    """Replay the canonical approved gate without consuming trial streams."""

    replay = Replay()
    replay.exact(
        "authorization canonical curve-table path",
        curve_table_path.resolve(),
        CURVE_TABLE_PATH.resolve(),
    )
    replay.exact(
        "authorization canonical config path",
        config_path.resolve(),
        CONFIG_PATH.resolve(),
    )
    curves = check_curve_table(load_json(curve_table_path), replay)
    config = load_json(config_path)
    bases, targets = check_config(
        config,
        curves,
        replay,
        curve_table_path=curve_table_path,
        preregistration_path=HERE / "PREREGISTRATION.md",
    )
    replay.exact("authorization base cell count", len(bases), 30)
    replay.exact("authorization target cell count", len(targets), 30)
    check_upstream_files(replay)
    check_no_outcomes(config, replay)
    authorization = check_approved_authorization(
        config=config,
        config_path=config_path,
        curve_table_path=curve_table_path,
        replay=replay,
        authorization_not_after=datetime.now(timezone.utc),
    )
    return {
        "validation_status": "AUTHORIZATION_PASS",
        "checks": replay.checks,
        "authorization_id": authorization["authorization_id"],
        "source_commit": authorization["source_commit"],
        "outcomes_present": False,
    }


def terminal_report(
    *,
    producer_terminal: str,
    resource_reason: str | None,
    cell_summaries: Sequence[dict[str, Any]],
    checks: int,
) -> dict[str, Any]:
    metrics = aggregate_curve_arms(cell_summaries)
    decisions = decision_metrics(cell_summaries)
    if producer_terminal == "PRODUCER_RESOURCE_EXHAUSTED_UNVALIDATED":
        if not isinstance(resource_reason, str) or not resource_reason:
            raise ValidationFailure("resource terminal requires a cause")
        return {
            "validation_status": "PASS",
            "checks": checks,
            "terminal_status": "PAUSE_INCONCLUSIVE",
            "cause": resource_reason,
            "opens_solver_slope_proposal": False,
            "h_new_retained": False,
            "curve_arm_metrics": metrics,
            "decision_metrics": decisions,
        }
    if producer_terminal != "PRODUCER_COMPLETE_UNVALIDATED":
        raise ValidationFailure("unknown producer terminal")
    terminal = classify_terminal(cell_summaries)
    if terminal not in TERMINAL_STATUSES:
        raise ValidationFailure("validator produced unknown terminal")
    return {
        "validation_status": "PASS",
        "checks": checks,
        "terminal_status": terminal,
        "opens_solver_slope_proposal": terminal in {
            "PROMOTE_TO_SOLVER_SLOPE_TEST",
            "CLASSIFY_AS_KNOWN_LOCAL_SIMPLIFICATION",
        },
        "h_new_retained": (
            terminal == "PROMOTE_TO_SOLVER_SLOPE_TEST"
            and decisions["h_new_signal"]
        ),
        "curve_arm_metrics": metrics,
        "decision_metrics": decisions,
    }


def check_resource_cell_prefix(
    cell_summaries: Sequence[dict[str, Any]], replay: Replay
) -> None:
    """Accept a verified completed prefix or one final partial cell.

    The producer checks CPU, wall-time, and RSS on the final trial too, so a
    resource limit can first be observed exactly when a cell becomes complete.
    """

    replay.require(bool(cell_summaries), "resource run has no cell summary")
    replay.require(
        len(cell_summaries) <= 30,
        "resource run has more cells than the frozen grid",
    )
    replay.require(
        all(cell["cell_complete"] for cell in cell_summaries[:-1]),
        "resource run has a nonterminal partial cell",
    )


def check_canonical_emission_paths(
    *,
    curve_table_path: Path,
    config_path: Path,
    manifest_path: Path,
    raw_path: Path,
    summary_path: Path,
    artifact_path: Path,
    sidecar_path: Path,
) -> None:
    supplied = (
        curve_table_path,
        config_path,
        manifest_path,
        raw_path,
        summary_path,
        artifact_path,
        sidecar_path,
    )
    frozen = (
        CURVE_TABLE_PATH,
        CONFIG_PATH,
        MANIFEST_PATH,
        RAW_PATH,
        SUMMARY_PATH,
        ARTIFACT_PATH,
        SIDECAR_PATH,
    )
    for actual, expected in zip(supplied, frozen):
        if actual.resolve() != expected.resolve():
            raise ValidationFailure(
                "--write-artifact requires every frozen canonical path; "
                f"{actual} does not resolve to {expected}"
            )


def validate_paths(
    *,
    curve_table_path: Path = CURVE_TABLE_PATH,
    config_path: Path = CONFIG_PATH,
    manifest_path: Path = MANIFEST_PATH,
    raw_path: Path = RAW_PATH,
    summary_path: Path = SUMMARY_PATH,
) -> dict[str, Any]:
    required = (
        curve_table_path,
        config_path,
        manifest_path,
        raw_path,
        summary_path,
    )
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise ValidationInconclusive("missing outcome files: " + ", ".join(missing))

    replay = Replay()
    curves = check_curve_table(load_json(curve_table_path), replay)
    config = load_json(config_path)
    bases, targets_by_cell = check_config(
        config,
        curves,
        replay,
        curve_table_path=curve_table_path,
        preregistration_path=HERE / "PREREGISTRATION.md",
    )
    manifest = load_json(manifest_path)
    check_manifest(
        manifest,
        curve_table_path=curve_table_path,
        config_path=config_path,
        replay=replay,
    )
    check_canonical_authorization(
        manifest=manifest,
        config=config,
        config_path=config_path,
        curve_table_path=curve_table_path,
        replay=replay,
    )
    events = read_canonical_jsonl(raw_path, replay)
    targets = config["targets"]
    bundles, raw_header, raw_run_summary = split_raw_events(
        events, targets, replay
    )
    replay.exact(
        "raw header",
        raw_header,
        {
            "event": "run_header",
            "raw_schema_version": "keyai-m16-fixed-target-raw-v1",
            **manifest,
        },
    )
    base_entries = {
        entry["cell_id"]: entry for entry in config["base_manifest"]
    }
    cell_summaries: list[dict[str, Any]] = []
    for target_entry in targets:
        current_cell = target_entry["cell_id"]
        if current_cell not in bundles:
            break
        cell_summaries.append(
            validate_cell_transcript(
                bundle=bundles[current_cell],
                target_entry=target_entry,
                shuffled_entry=targets_by_cell[
                    target_entry["shuffled_target_cell_id"]
                ],
                base_entry=base_entries[current_cell],
                factor_base=bases[current_cell],
                curve=curves[target_entry["curve_id"]],
                config=config,
                replay=replay,
            )
        )
    replay.exact(
        "raw cell prefix",
        list(bundles),
        [entry["cell_id"] for entry in targets[:len(bundles)]],
    )
    all_base_operation_counts: list[dict[str, int]] = []
    for entry in config["base_manifest"]:
        _, metadata = reconstruct_factor_base(
            curve=curves[entry["curve_id"]],
            arm=entry["arm"],
            seed=entry["seed"],
            prefix=PRNG_PREFIX,
            size=config["factor_base_size"],
        )
        all_base_operation_counts.append(metadata["operation_counts"])
    expected_total_operations = sum_operation_counts(
        all_base_operation_counts
        + [cell["operation_counts"] for cell in cell_summaries]
    )

    replay.exact(
        "raw run summary keys",
        set(raw_run_summary),
        {
            "event",
            "run_id",
            "total_primary_trials",
            "cell_count",
            "operation_counts",
            "terminal_status",
            "resource_exhausted_reason",
            "finished_utc",
        },
    )
    replay.exact("raw run id", raw_run_summary["run_id"], manifest["run_id"])
    actual_primary_trials = sum(
        cell["counts"]["attempts"] for cell in cell_summaries
    )
    replay.exact(
        "raw primary trial count",
        raw_run_summary["total_primary_trials"],
        actual_primary_trials,
    )
    replay.exact(
        "raw cell count", raw_run_summary["cell_count"], len(cell_summaries)
    )
    producer_terminal = raw_run_summary["terminal_status"]
    replay.require(
        producer_terminal in {
            "PRODUCER_COMPLETE_UNVALIDATED",
            "PRODUCER_RESOURCE_EXHAUSTED_UNVALIDATED",
        },
        "unknown producer terminal status",
    )
    resource_reason = raw_run_summary["resource_exhausted_reason"]
    if producer_terminal == "PRODUCER_COMPLETE_UNVALIDATED":
        replay.exact("complete run resource reason", resource_reason, None)
        replay.exact("complete run cell count", len(cell_summaries), 30)
        replay.require(
            all(cell["cell_complete"] for cell in cell_summaries),
            "complete run contains partial cell",
        )
        replay.exact(
            "complete run primary trial count",
            actual_primary_trials,
            config["resource_budget"]["max_primary_trials"],
        )
    else:
        replay.require(
            isinstance(resource_reason, str) and bool(resource_reason),
            "resource terminal requires nonempty reason",
        )
        check_resource_cell_prefix(cell_summaries, replay)
    check_operation_counts(
        raw_run_summary["operation_counts"], "raw run operation counts", replay
    )
    replay.exact(
        "raw run operation aggregation",
        raw_run_summary["operation_counts"],
        expected_total_operations,
    )
    finished = parse_utc_timestamp(
        raw_run_summary["finished_utc"], "raw run finished", replay
    )
    started = parse_utc_timestamp(
        manifest["chronology"]["run_started_utc"], "raw run started", replay
    )
    replay.require(started <= finished, "run finished before it started")

    summary = load_json(summary_path)
    replay.require(isinstance(summary, dict), "summary: expected object")
    replay.exact(
        "summary keys",
        set(summary),
        {
            "schema_version",
            "hypothesis_id",
            "run_id",
            "bindings",
            "chronology",
            "raw_files",
            "cells",
            "totals",
            "resource_usage",
            "terminal_status",
            "resource_exhausted_reason",
        },
    )
    replay.exact(
        "summary.schema_version",
        summary["schema_version"],
        "keyai-m16-fixed-target-summary-v1",
    )
    replay.exact("summary.hypothesis_id", summary["hypothesis_id"], HYPOTHESIS_ID)
    replay.exact("summary.run_id", summary["run_id"], manifest["run_id"])
    replay.exact("summary.bindings", summary["bindings"], manifest["bindings"])
    replay.exact(
        "summary.chronology",
        summary["chronology"],
        {
            **manifest["chronology"],
            "run_finished_utc": raw_run_summary["finished_utc"],
        },
    )
    check_raw_file_binding(
        raw_path,
        summary["raw_files"],
        config["output_contract"]["raw_jsonl"],
        replay,
    )
    replay.exact(
        "summary.cells",
        summary["cells"],
        [
            {key: value for key, value in cell.items()
             if key != "_validator_metrics"}
            for cell in cell_summaries
        ],
    )
    replay.exact(
        "summary.totals",
        summary["totals"],
        {
            "primary_trials": actual_primary_trials,
            "operations": raw_run_summary["operation_counts"],
        },
    )
    check_resource_usage(
        summary["resource_usage"],
        budget=config["resource_budget"],
        resource_reason=resource_reason,
        replay=replay,
    )
    replay.exact("summary producer terminal", summary["terminal_status"],
                 producer_terminal)
    replay.exact(
        "summary resource reason",
        summary["resource_exhausted_reason"],
        resource_reason,
    )
    check_upstream_files(replay)
    report = terminal_report(
        producer_terminal=producer_terminal,
        resource_reason=resource_reason,
        cell_summaries=cell_summaries,
        checks=replay.checks,
    )
    report["validated_artifact"] = build_validated_artifact(
        report=report,
        manifest=manifest,
        summary=summary,
        config=config,
        manifest_path=manifest_path,
        raw_path=raw_path,
        summary_path=summary_path,
    )
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--curve-table", type=Path, default=CURVE_TABLE_PATH)
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--raw", type=Path, default=RAW_PATH)
    parser.add_argument("--summary", type=Path, default=SUMMARY_PATH)
    parser.add_argument("--artifact", type=Path, default=ARTIFACT_PATH)
    parser.add_argument("--sidecar", type=Path, default=SIDECAR_PATH)
    phase = parser.add_mutually_exclusive_group()
    phase.add_argument(
        "--readiness",
        action="store_true",
        help="validate frozen inputs and require outcome files to be absent",
    )
    phase.add_argument(
        "--authorization",
        action="store_true",
        help=(
            "independently verify the exact canonical approved gate while "
            "requiring outcome files to be absent"
        ),
    )
    parser.add_argument(
        "--write-artifact",
        action="store_true",
        help=(
            "after a complete PASS replay, create artifact.json and "
            "artifact.sha256 without overwriting either"
        ),
    )
    args = parser.parse_args(argv)
    try:
        if (args.readiness or args.authorization) and args.write_artifact:
            raise ValidationFailure(
                "--write-artifact is forbidden in pre-execution modes"
            )
        if args.write_artifact:
            check_canonical_emission_paths(
                curve_table_path=args.curve_table,
                config_path=args.config,
                manifest_path=args.manifest,
                raw_path=args.raw,
                summary_path=args.summary,
                artifact_path=args.artifact,
                sidecar_path=args.sidecar,
            )
        if args.readiness:
            report = readiness_check(
                curve_table_path=args.curve_table,
                config_path=args.config,
            )
        elif args.authorization:
            report = authorization_check(
                curve_table_path=args.curve_table,
                config_path=args.config,
            )
        else:
            report = validate_paths(
                curve_table_path=args.curve_table,
                config_path=args.config,
                manifest_path=args.manifest,
                raw_path=args.raw,
                summary_path=args.summary,
            )
            artifact_document = report["validated_artifact"]
            if args.write_artifact:
                emit_validated_artifact(
                    artifact_document, args.artifact, args.sidecar
                )
                verify_validated_artifact(
                    artifact_document,
                    args.artifact,
                    args.sidecar,
                    Replay(),
                )
            elif args.artifact.exists() or args.sidecar.exists():
                verify_validated_artifact(
                    artifact_document,
                    args.artifact,
                    args.sidecar,
                    Replay(),
                )
    except ValidationInconclusive as exc:
        print(f"VALIDATION: INCONCLUSIVE: {exc}")
        return 2
    except (
        ValidationFailure,
        OSError,
        ValueError,
        TypeError,
        KeyError,
        IndexError,
    ) as exc:
        print(f"VALIDATION: FAIL: {exc}")
        return 1
    if args.readiness:
        print(f"READINESS_PASS: {report['checks']} independent checks")
    elif args.authorization:
        print(
            "AUTHORIZATION_PASS: "
            f"{report['checks']} independent checks; "
            f"authorization_id={report['authorization_id']}; "
            f"source_commit={report['source_commit']}; "
            "outcomes_present=false"
        )
    else:
        if report["validation_status"] == "INCONCLUSIVE":
            print(
                "VALIDATION: INCONCLUSIVE: "
                f"{report['checks']} independent checks; "
                f"terminal={report['terminal_status']}; "
                f"cause={report['cause']}"
            )
            return 2
        print(
            "VALIDATION: PASS: "
            f"{report['checks']} independent checks; "
            f"terminal={report['terminal_status']}; "
            f"h_new_retained={str(report['h_new_retained']).lower()}; "
            "artifact="
            + (
                "written-and-verified"
                if args.write_artifact
                else (
                    "verified"
                    if args.artifact.exists() and args.sidecar.exists()
                    else "not-written"
                )
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
