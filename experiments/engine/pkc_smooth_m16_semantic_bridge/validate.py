#!/usr/bin/env python3
"""Independently replay the M16 affine-semantic bridge certificate.

The validator imports neither the producer nor its helpers.  It rechecks the
finite fields, point counts, group arithmetic, source-root membership, local
S3 roots, reachable prefix states, S4 Sylvester boundary, recovery contract,
canonical JSON, committed digest, and non-authorizing terminal disposition.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


EXPECTED_D = 564_522
EXPECTED_M = 16
EXPECTED_FACTORS = [2, 3, 7, 13_441]
EXPECTED_CONTROL_P = 564_523
EXPECTED_CURVE_ORDER = 564_469
EXPECTED_ORDER_FACTORS = [163, 3_463]
EXPECTED_SUBGROUP_ORDER = 3_463
EXPECTED_SEED = (2, 100_588)
EXPECTED_BASE = (555_781, 547_362)
EXPECTED_REPEATED = (169_010, 177_754)
EXPECTED_DOUBLED_REPEATED = (210_845, 520_607)
EXPECTED_TARGET = (442_919, 534_774)
EXPECTED_M16_DESK_SHA256 = (
    "59596c3c59f5389c49742ba4a26d500445557ee6398d6aaad63c7995a93242f7"
)
EXPECTED_M16_DESK_PATH = (
    "experiments/engine/pkc_smooth_m16_symbolic_desk/artifact.json"
)
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]

Point = tuple[int, int] | None
HOMOGENEOUS_S3_TERMS = {
    (2, 0, 2, 0, 0, 2): 1,
    (2, 0, 0, 2, 2, 0): 1,
    (0, 2, 2, 0, 2, 0): 1,
    (2, 0, 1, 1, 1, 1): -2,
    (1, 1, 2, 0, 1, 1): -2,
    (1, 1, 1, 1, 2, 0): -2,
    (1, 1, 0, 2, 0, 2): -28,
    (0, 2, 1, 1, 0, 2): -28,
    (0, 2, 0, 2, 1, 1): -28,
}


class Replay:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def expect(self, path: str, actual: Any, expected: Any) -> None:
        if actual != expected:
            self.failures.append(
                f"{path}: expected {expected!r}, observed {actual!r}"
            )

    def require_dict(self, path: str, value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            self.failures.append(f"{path}: expected object")
            return {}
        return value

    def require_list(self, path: str, value: Any) -> list[Any]:
        if not isinstance(value, list):
            self.failures.append(f"{path}: expected array")
            return []
        return value


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def exact_prime_check(value: int) -> bool:
    if value < 2:
        return False
    for divisor in range(2, math.isqrt(value) + 1):
        if value % divisor == 0:
            return False
    return True


def inverse_mod(value: int, modulus: int) -> int:
    old_r, r = value % modulus, modulus
    old_s, s = 1, 0
    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
    if old_r != 1:
        raise ZeroDivisionError("noninvertible denominator")
    return old_s % modulus


def on_curve(point: Point, prime: int) -> bool:
    if point is None:
        return True
    x, y = point
    return (y * y - x**3 - 7) % prime == 0


def negate(point: Point, prime: int) -> Point:
    if point is None:
        return None
    return point[0], (-point[1]) % prime


def add(left: Point, right: Point, prime: int) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    if not on_curve(left, prime) or not on_curve(right, prime):
        raise ValueError("off-curve input")
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % prime == 0:
        return None
    if left == right:
        denominator = (2 * y1) % prime
        if denominator == 0:
            return None
        slope = 3 * x1 * x1 * inverse_mod(denominator, prime)
    else:
        slope = (y2 - y1) * inverse_mod(x2 - x1, prime)
    slope %= prime
    x3 = (slope * slope - x1 - x2) % prime
    y3 = (slope * (x1 - x3) - y1) % prime
    result = (x3, y3)
    if not on_curve(result, prime):
        raise AssertionError("group operation left the curve")
    return result


def multiply(scalar: int, point: Point, prime: int) -> Point:
    if scalar < 0:
        return multiply(-scalar, negate(point, prime), prime)
    result: Point = None
    addend = point
    for bit in reversed(format(scalar, "b")):
        if bit == "1":
            result = add(result, addend, prime)
        addend = add(addend, addend, prime)
    return result


def record_to_point(
    path: str, value: Any, replay: Replay
) -> Point:
    record = replay.require_dict(path, value)
    kind = record.get("kind")
    if kind == "identity":
        return None
    if kind != "affine":
        replay.failures.append(f"{path}.kind: unsupported point kind")
        return None
    x = record.get("x")
    y = record.get("y")
    if not isinstance(x, int) or not isinstance(y, int):
        replay.failures.append(f"{path}: affine coordinates must be integers")
        return None
    return x, y


def point_count(prime: int) -> tuple[int, list[int]]:
    count = 1
    two_torsion: list[int] = []
    for x in range(prime):
        rhs = (x**3 + 7) % prime
        if rhs == 0:
            count += 1
            two_torsion.append(x)
            continue
        character = pow(rhs, (prime - 1) // 2, prime)
        if character == 1:
            count += 2
        elif character != prime - 1:
            raise AssertionError("Euler criterion failed")
    return count, two_torsion


def s3_coefficients(
    prime: int, x1: int, x2: int, a: int = 0, b: int = 7
) -> list[int]:
    leading = (x1 - x2) ** 2 % prime
    linear = (
        -2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b)
    ) % prime
    constant = (
        (x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)
    ) % prime
    return [leading, linear, constant]


def evaluate(coefficients: list[int], value: int, prime: int) -> int:
    result = 0
    for coefficient in coefficients:
        result = (result * value + coefficient) % prime
    return result


def sylvester(left: list[int], right: list[int]) -> list[list[int]]:
    return [
        [left[0], left[1], left[2], 0],
        [0, left[0], left[1], left[2]],
        [right[0], right[1], right[2], 0],
        [0, right[0], right[1], right[2]],
    ]


def determinant_laplace(matrix: list[list[int]]) -> int:
    if len(matrix) == 1:
        return matrix[0][0]
    total = 0
    for column, entry in enumerate(matrix[0]):
        minor = [
            row[:column] + row[column + 1 :]
            for row in matrix[1:]
        ]
        total += (
            (-1 if column % 2 else 1)
            * entry
            * determinant_laplace(minor)
        )
    return total


def s3_homogeneous(
    prime: int,
    x1: int,
    z1: int,
    x2: int,
    z2: int,
    x3: int,
    z3: int,
) -> int:
    values = (x1, z1, x2, z2, x3, z3)
    return sum(
        coefficient
        * math.prod(
            value**exponent
            for value, exponent in zip(values, exponents, strict=True)
        )
        for exponents, coefficient in HOMOGENEOUS_S3_TERMS.items()
    ) % prime


def canonical_scalar(value: int) -> int:
    residue = value % EXPECTED_SUBGROUP_ORDER
    return min(residue, (-residue) % EXPECTED_SUBGROUP_ORDER)


def rebuild_layers() -> list[list[int]]:
    states = {100}
    result = [[100]]
    for _ in range(14):
        states = {
            canonical_scalar(state + delta)
            for state in states
            for delta in (-1, 1)
        }
        states.discard(0)
        result.append(sorted(states))
    return result


def replay_recovery_preimages() -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    per_rank: list[dict[str, int]] = []
    pairs = list(itertools.combinations(range(EXPECTED_M), 2))
    for rank, repeated_positions in enumerate(pairs):
        scalars = [1] * EXPECTED_M
        for position in repeated_positions:
            scalars[position] = 50

        right_masks: dict[int, list[int]] = {}
        for right_mask in range(256):
            value = 0
            for offset in range(8):
                sign = 1 if right_mask & (1 << offset) else -1
                value += sign * scalars[8 + offset]
            right_masks.setdefault(value, []).append(right_mask)

        rank_records: list[dict[str, Any]] = []
        for left_mask in range(128):
            left_value = scalars[0]
            for offset in range(7):
                sign = 1 if left_mask & (1 << offset) else -1
                left_value += sign * scalars[1 + offset]
            for orientation in (-1, 1):
                needed = orientation * 14 - left_value
                for right_mask in right_masks.get(needed, []):
                    mask = left_mask | (right_mask << 7)
                    running = scalars[0]
                    identity_prefixes: list[int] = []
                    for index in range(1, EXPECTED_M):
                        sign = 1 if mask & (1 << (index - 1)) else -1
                        running += sign * scalars[index]
                        prefix_size = index + 1
                        if (
                            prefix_size <= EXPECTED_M - 1
                            and running % EXPECTED_SUBGROUP_ORDER == 0
                        ):
                            identity_prefixes.append(prefix_size)
                    record = {
                        "identity_prefix_sizes": identity_prefixes,
                        "permutation_rank": rank,
                        "repeated_positions_zero_based": list(
                            repeated_positions
                        ),
                        "sign_mask_tail_15": mask,
                        "target_orientation": orientation,
                    }
                    rank_records.append(record)
                    records.append(record)
        per_rank.append(
            {
                "affine_admissible": sum(
                    not record["identity_prefix_sizes"]
                    for record in rank_records
                ),
                "direct": len(rank_records),
                "identity_blocked": sum(
                    bool(record["identity_prefix_sizes"])
                    for record in rank_records
                ),
                "rank": rank,
            }
        )

    records.sort(
        key=lambda item: (
            item["permutation_rank"],
            item["sign_mask_tail_15"],
            item["target_orientation"],
        )
    )
    admissible = [
        record for record in records if not record["identity_prefix_sizes"]
    ]
    blocked = [
        record for record in records if record["identity_prefix_sizes"]
    ]
    row = {
        "dropped_zero_coefficients": [
            {"basis": "repeated_50P", "coefficient_mod_order": 0}
        ],
        "factor_coefficients": [
            {"basis": "base_P", "coefficient_mod_order": 14}
        ],
        "target_coefficient_mod_order": EXPECTED_SUBGROUP_ORDER - 1,
        "verification": "[14]P - R = identity",
    }
    return {
        "accepted_record_sha256": hashlib.sha256(
            canonical_bytes(records)
        ).hexdigest(),
        "admissible": admissible,
        "affine_admissible_record_sha256": hashlib.sha256(
            canonical_bytes(admissible)
        ).hexdigest(),
        "blocked": blocked,
        "per_rank_counts_sha256": hashlib.sha256(
            canonical_bytes(per_rank)
        ).hexdigest(),
        "records": records,
        "row": row,
        "row_sha256": hashlib.sha256(canonical_bytes(row)).hexdigest(),
        "unique_orderings": len(pairs),
    }


def check_hash(
    artifact_bytes: bytes, hash_path: Path, replay: Replay
) -> None:
    try:
        text = hash_path.read_text(encoding="ascii")
    except (FileNotFoundError, UnicodeDecodeError) as error:
        replay.failures.append(f"artifact.sha256 unreadable: {error}")
        return
    match = re.fullmatch(r"([0-9a-f]{64})  artifact\.json\n", text)
    if match is None:
        replay.failures.append("artifact.sha256 has noncanonical format")
        return
    replay.expect(
        "artifact.sha256",
        match.group(1),
        hashlib.sha256(artifact_bytes).hexdigest(),
    )


def check_metadata(document: dict[str, Any], replay: Replay) -> None:
    replay.expect("schema_version", document.get("schema_version"), "1.0")
    replay.expect(
        "artifact_id",
        document.get("artifact_id"),
        "PKC-SMOOTH-M16-SEMANTIC-BRIDGE-001",
    )
    replay.expect(
        "kind",
        document.get("kind"),
        "deterministic_nonexperimental_semantic_counterexample",
    )
    scope = replay.require_dict("scope", document.get("scope"))
    excluded = replay.require_list("scope.excluded", scope.get("excluded"))
    for phrase in (
        "S17 expansion or evaluation at the M16 witness",
        "materialized recursive or membership polynomial system",
        "exact-target secp256k1 relation search",
        "solving-degree, rank, runtime, or security claim",
        "hypothesis retention, experiment authorization, or route promotion",
    ):
        if phrase not in excluded:
            replay.failures.append(f"scope.excluded lacks {phrase!r}")


def check_source_scope(document: dict[str, Any], replay: Replay) -> None:
    scope = replay.require_dict("source_scope", document.get("source_scope"))
    expected_paths = {
        "curve_full_group": "Ecdlp/Proved/CurveFullGroup.lean",
        "glv_eigenvalue": "Ecdlp/Proved/GlvSubgroupEigenvalue.lean",
        "glv_orbit": "Ecdlp/Proved/GlvOrbit.lean",
        "m16_desk_artifact": EXPECTED_M16_DESK_PATH,
        "primary_claim_extract": (
            "data/source_claim_extracts/petit_kosters_messeng2016.json"
        ),
        "semaev_four": "Ecdlp/Proved/SemaevFour.lean",
        "semaev_three": "Ecdlp/Proved/SemaevThree.lean",
    }
    for field, expected in expected_paths.items():
        replay.expect(f"source_scope.{field}", scope.get(field), expected)
        if not (REPO_ROOT / expected).is_file():
            replay.failures.append(
                f"source_scope.{field}: referenced file is missing"
            )
    replay.expect(
        "source_scope.m16_desk_artifact_sha256",
        scope.get("m16_desk_artifact_sha256"),
        EXPECTED_M16_DESK_SHA256,
    )
    try:
        desk_bytes = (REPO_ROOT / EXPECTED_M16_DESK_PATH).read_bytes()
    except FileNotFoundError:
        replay.failures.append("referenced M16 desk artifact is missing")
    else:
        replay.expect(
            "source_scope.replayed_m16_desk_sha256",
            hashlib.sha256(desk_bytes).hexdigest(),
            EXPECTED_M16_DESK_SHA256,
        )
    replay.expect(
        "source_scope.source_claim_ids",
        scope.get("source_claim_ids"),
        [
            "SC-GLV-ENDOMORPHISM",
            "SC-GLV-ENDOMORPHISM-NONTRIVIAL",
            "SC-PKC-SMOOTH-SUBGROUP",
            "SC-SECP-NO-TWO-TORSION",
            "SC-SEMAEV-RELATION-SEMANTICS",
            "SC-PKC-M16-SYMBOLIC-DESK-RESULT",
        ],
    )


def check_control_counterexample(
    document: dict[str, Any], replay: Replay
) -> None:
    counterexample = replay.require_dict(
        "control_field_m16_counterexample",
        document.get("control_field_m16_counterexample"),
    )
    field = replay.require_dict(
        "control_field.field", counterexample.get("field")
    )
    replay.expect("control_field.p", field.get("p"), EXPECTED_CONTROL_P)
    replay.expect("control_field.D", field.get("D"), EXPECTED_D)
    replay.expect(
        "control_field.factor_chain",
        field.get("factor_chain"),
        EXPECTED_FACTORS,
    )
    replay.expect(
        "control_field.factor_product",
        math.prod(EXPECTED_FACTORS),
        EXPECTED_D,
    )
    replay.expect(
        "control_field.multiplicative_group_order",
        field.get("multiplicative_group_order"),
        EXPECTED_D,
    )
    replay.expect(
        "control_field.p_equals_D_plus_one",
        EXPECTED_CONTROL_P,
        EXPECTED_D + 1,
    )
    replay.expect(
        "control_field.p_prime",
        exact_prime_check(EXPECTED_CONTROL_P),
        True,
    )

    curve = replay.require_dict(
        "control_field.curve", counterexample.get("curve")
    )
    replay.expect("control_field.curve.a", curve.get("a"), 0)
    replay.expect("control_field.curve.b", curve.get("b"), 7)
    discriminant = (-16 * 27 * 49) % EXPECTED_CONTROL_P
    replay.expect(
        "control_field.curve.discriminant_mod_p",
        curve.get("discriminant_mod_p"),
        discriminant,
    )
    if discriminant == 0:
        replay.failures.append("control curve is singular")
    order, two_torsion = point_count(EXPECTED_CONTROL_P)
    replay.expect(
        "control_field.curve.order",
        curve.get("order"),
        order,
    )
    replay.expect(
        "control_field.curve.order.expected",
        order,
        EXPECTED_CURVE_ORDER,
    )
    replay.expect(
        "control_field.curve.order_factorization",
        curve.get("order_factorization"),
        EXPECTED_ORDER_FACTORS,
    )
    replay.expect(
        "control_field.curve.order_factor_product",
        math.prod(EXPECTED_ORDER_FACTORS),
        order,
    )
    for factor in EXPECTED_ORDER_FACTORS:
        replay.expect(
            f"control_field.curve.order_factor_{factor}_prime",
            exact_prime_check(factor),
            True,
        )
    replay.expect(
        "control_field.curve.rational_two_torsion_x",
        curve.get("rational_two_torsion_x"),
        two_torsion,
    )
    replay.expect(
        "control_field.curve.no_two_torsion",
        two_torsion,
        [],
    )

    points = replay.require_dict(
        "control_field.points", counterexample.get("points")
    )
    seed = record_to_point("control_field.points.seed_T", points.get("seed_T"), replay)
    base = record_to_point("control_field.points.base_P", points.get("base_P"), replay)
    repeated = record_to_point(
        "control_field.points.repeated_50P",
        points.get("repeated_50P"),
        replay,
    )
    doubled = record_to_point(
        "control_field.points.doubled_repeated_100P",
        points.get("doubled_repeated_100P"),
        replay,
    )
    target = record_to_point(
        "control_field.points.target_14P",
        points.get("target_14P"),
        replay,
    )
    replay.expect("control_field.seed", seed, EXPECTED_SEED)
    replay.expect("control_field.base", base, EXPECTED_BASE)
    replay.expect("control_field.repeated", repeated, EXPECTED_REPEATED)
    replay.expect(
        "control_field.doubled_repeated",
        doubled,
        EXPECTED_DOUBLED_REPEATED,
    )
    replay.expect("control_field.target", target, EXPECTED_TARGET)
    for label, point in (
        ("seed", seed),
        ("base", base),
        ("repeated", repeated),
        ("doubled", doubled),
        ("target", target),
    ):
        replay.expect(
            f"control_field.points.{label}.on_curve",
            on_curve(point, EXPECTED_CONTROL_P),
            True,
        )
    replay.expect(
        "control_field.base_construction",
        multiply(163, seed, EXPECTED_CONTROL_P),
        base,
    )
    replay.expect(
        "control_field.base_order_multiple",
        multiply(EXPECTED_SUBGROUP_ORDER, base, EXPECTED_CONTROL_P),
        None,
    )
    replay.expect(
        "control_field.base_nonidentity",
        base is not None,
        True,
    )
    replay.expect(
        "control_field.repeated_scalar",
        multiply(50, base, EXPECTED_CONTROL_P),
        repeated,
    )
    replay.expect(
        "control_field.doubled_scalar",
        multiply(100, base, EXPECTED_CONTROL_P),
        doubled,
    )
    replay.expect(
        "control_field.target_scalar",
        multiply(14, base, EXPECTED_CONTROL_P),
        target,
    )

    membership = replay.require_dict(
        "control_field.membership_checks",
        counterexample.get("membership_checks"),
    )
    for label, point in (
        ("base", base),
        ("repeated", repeated),
        ("doubled_repeated", doubled),
        ("target", target),
    ):
        if point is None:
            continue
        replay.expect(
            f"control_field.membership.{label}_x_nonzero",
            point[0] != 0,
            True,
        )
        replay.expect(
            f"control_field.membership.{label}_x_to_D",
            membership.get(f"{label}_x_to_D"),
            pow(point[0], EXPECTED_D, EXPECTED_CONTROL_P),
        )
        replay.expect(
            f"control_field.membership.{label}_root",
            pow(point[0], EXPECTED_D, EXPECTED_CONTROL_P),
            1,
        )

    direct = replay.require_dict(
        "control_field.direct_relation_witness",
        counterexample.get("direct_relation_witness"),
    )
    replay.expect(
        "control_field.direct.leaf_scalars",
        direct.get("leaf_scalars"),
        [50, 50] + [1] * 14,
    )
    replay.expect(
        "control_field.direct.leaf_signs",
        direct.get("leaf_signs"),
        [1, -1] + [1] * 14,
    )
    replay.expect(
        "control_field.direct.target_scalar",
        direct.get("target_scalar"),
        14,
    )
    replay.expect(
        "control_field.direct.target_sign",
        direct.get("target_sign"),
        -1,
    )
    relation: Point = None
    for scalar, sign in zip(
        direct.get("leaf_scalars", []),
        direct.get("leaf_signs", []),
        strict=False,
    ):
        relation = add(
            relation,
            multiply(sign * scalar, base, EXPECTED_CONTROL_P),
            EXPECTED_CONTROL_P,
        )
    relation = add(
        relation,
        multiply(
            direct.get("target_sign", 0)
            * direct.get("target_scalar", 0),
            base,
            EXPECTED_CONTROL_P,
        ),
        EXPECTED_CONTROL_P,
    )
    replay.expect("control_field.direct.group_sum", relation, None)
    direct_scope = direct.get("scope")
    if not isinstance(direct_scope, str) or (
        "S17 is not expanded or evaluated" not in direct_scope
    ):
        replay.failures.append(
            "control-field witness must not claim an S17 evaluation"
        )

    obstruction = replay.require_dict(
        "control_field.recursive_affine_obstruction",
        counterexample.get("recursive_affine_obstruction"),
    )
    if repeated is not None and doubled is not None:
        first_coefficients = s3_coefficients(
            EXPECTED_CONTROL_P, repeated[0], repeated[0]
        )
        replay.expect(
            "control_field.recursive.first_slice_coefficients",
            obstruction.get("first_slice_coefficients_z2_z1_z0"),
            first_coefficients,
        )
        replay.expect(
            "control_field.recursive.first_slice_linear",
            first_coefficients[0],
            0,
        )
        if first_coefficients[1] == 0:
            replay.failures.append(
                "control repeated-x slice unexpectedly lost linear degree"
            )
        else:
            unique_root = (
                -first_coefficients[2]
                * inverse_mod(first_coefficients[1], EXPECTED_CONTROL_P)
            ) % EXPECTED_CONTROL_P
            replay.expect(
                "control_field.recursive.first_slice_unique_root",
                obstruction.get("first_slice_unique_root"),
                unique_root,
            )
            replay.expect(
                "control_field.recursive.first_slice_doubling_root",
                unique_root,
                doubled[0],
            )

    layers = rebuild_layers()
    replay.expect(
        "control_field.recursive.reachable_layers",
        obstruction.get("reachable_scalar_classes_after_each_base_leaf"),
        layers,
    )
    replay.expect(
        "control_field.recursive.terminal_scalar_classes",
        obstruction.get("terminal_scalar_classes"),
        list(range(86, 115, 2)),
    )
    replay.expect(
        "control_field.recursive.target_scalar_class",
        obstruction.get("target_scalar_class"),
        14,
    )
    replay.expect(
        "control_field.recursive.terminal_intersection",
        obstruction.get("terminal_intersection_with_target"),
        [],
    )

    checked_parents = 0
    checked_roots = 0
    if base is not None:
        for layer in layers[:-1]:
            for scalar in layer:
                parent = multiply(scalar, base, EXPECTED_CONTROL_P)
                plus = multiply(scalar + 1, base, EXPECTED_CONTROL_P)
                minus = multiply(scalar - 1, base, EXPECTED_CONTROL_P)
                if parent is None or plus is None or minus is None:
                    replay.failures.append(
                        "control transition unexpectedly reached identity"
                    )
                    continue
                if parent[0] == base[0]:
                    replay.failures.append(
                        "control transition unexpectedly entered repeated-x fiber"
                    )
                    continue
                coefficients = s3_coefficients(
                    EXPECTED_CONTROL_P, parent[0], base[0]
                )
                replay.expect(
                    f"control.transition.{scalar}.quadratic",
                    coefficients[0] != 0,
                    True,
                )
                predicted_roots = {plus[0], minus[0]}
                replay.expect(
                    f"control.transition.{scalar}.root_count",
                    len(predicted_roots),
                    2,
                )
                for root in predicted_roots:
                    replay.expect(
                        f"control.transition.{scalar}.root_{root}",
                        evaluate(
                            coefficients, root, EXPECTED_CONTROL_P
                        ),
                        0,
                    )
                checked_parents += 1
                checked_roots += len(predicted_roots)
    replay.expect(
        "control_field.recursive.checked_layer_indexed_parent_occurrences",
        obstruction.get("checked_layer_indexed_parent_occurrences"),
        checked_parents,
    )
    replay.expect(
        "control_field.recursive.checked_layer_indexed_root_evaluations",
        obstruction.get("checked_layer_indexed_root_evaluations"),
        checked_roots,
    )
    unique_parent_classes = len(
        set().union(*(set(layer) for layer in layers[:-1]))
    )
    replay.expect(
        "control_field.recursive.unique_parent_scalar_classes",
        obstruction.get("unique_parent_scalar_classes"),
        unique_parent_classes,
    )
    replay.expect(
        "control_field.recursive.unique_parent_scalar_classes.exact",
        unique_parent_classes,
        27,
    )
    replay.expect(
        "control_field.recursive.root_evaluations_for_unique_parent_classes",
        obstruction.get("root_evaluations_for_unique_parent_classes"),
        2 * unique_parent_classes,
    )


def check_small_boundary(document: dict[str, Any], replay: Replay) -> None:
    witness = replay.require_dict(
        "small_no_rational_two_torsion_resultant_boundary_witness",
        document.get(
            "small_no_rational_two_torsion_resultant_boundary_witness"
        ),
    )
    curve = replay.require_dict("small.curve", witness.get("curve"))
    replay.expect("small.p", curve.get("p"), 13)
    replay.expect("small.p_prime", exact_prime_check(13), True)
    replay.expect(
        "small.discriminant_nonzero",
        (-16 * 27 * 49) % 13 != 0,
        True,
    )
    _, two_torsion = point_count(13)
    replay.expect(
        "small.rational_two_torsion_x",
        curve.get("rational_two_torsion_x"),
        two_torsion,
    )
    replay.expect("small.no_two_torsion", two_torsion, [])

    points = replay.require_list(
        "small.direct_signed_points", witness.get("direct_signed_points")
    )
    decoded = [
        record_to_point(f"small.direct_signed_points[{index}]", value, replay)
        for index, value in enumerate(points)
    ]
    replay.expect(
        "small.direct_signed_points.decoded",
        decoded,
        [(7, 5), (7, 8), (8, 5), (8, 8)],
    )
    group_sum: Point = None
    for point in decoded:
        group_sum = add(group_sum, point, 13)
    replay.expect("small.signed_group_sum", group_sum, None)

    left = s3_coefficients(13, 7, 7)
    right = s3_coefficients(13, 8, 8)
    left_roots = [value for value in range(13) if evaluate(left, value, 13) == 0]
    right_roots = [
        value for value in range(13) if evaluate(right, value, 13) == 0
    ]
    matrix = sylvester(left, right)
    resultant = determinant_laplace(matrix) % 13
    replay.expect(
        "small.left_slice_coefficients",
        witness.get("left_slice_coefficients_z2_z1_z0"),
        left,
    )
    replay.expect(
        "small.right_slice_coefficients",
        witness.get("right_slice_coefficients_z2_z1_z0"),
        right,
    )
    replay.expect("small.left_slice_roots", witness.get("left_slice_roots"), left_roots)
    replay.expect(
        "small.right_slice_roots",
        witness.get("right_slice_roots"),
        right_roots,
    )
    replay.expect(
        "small.recursive_common_roots",
        witness.get("recursive_common_roots"),
        sorted(set(left_roots) & set(right_roots)),
    )
    replay.expect(
        "small.recursive_common_roots.empty",
        sorted(set(left_roots) & set(right_roots)),
        [],
    )
    replay.expect("small.sylvester_matrix", witness.get("sylvester_matrix"), matrix)
    replay.expect(
        "small.fixed_size_s4_resultant",
        witness.get("fixed_size_s4_resultant"),
        resultant,
    )
    replay.expect("small.fixed_size_s4_resultant.zero", resultant, 0)


def check_extension_membership_witness(
    document: dict[str, Any], replay: Replay
) -> None:
    witness = replay.require_dict(
        "extension_field_membership_witness",
        document.get("extension_field_membership_witness"),
    )
    field = replay.require_dict(
        "extension_field.field", witness.get("field")
    )
    replay.expect("extension_field.p", field.get("p"), 5)
    replay.expect(
        "extension_field.characteristic_greater_than_three",
        field.get("characteristic_greater_than_three"),
        True,
    )
    replay.expect("extension_field.D", field.get("D"), EXPECTED_D)
    replay.expect(
        "extension_field.D_mod_group_order",
        field.get("D_mod_multiplicative_group_order"),
        EXPECTED_D % 4,
    )
    replay.expect(
        "extension_field.gcd_D_group_order",
        field.get("gcd_D_multiplicative_group_order"),
        math.gcd(EXPECTED_D, 4),
    )
    membership_roots = [
        value
        for value in range(1, 5)
        if pow(value, EXPECTED_D, 5) == 1
    ]
    replay.expect(
        "extension_field.membership_roots",
        field.get("membership_roots"),
        membership_roots,
    )
    replay.expect(
        "extension_field.membership_roots.exact",
        membership_roots,
        [1, 4],
    )

    curve = replay.require_dict(
        "extension_field.curve", witness.get("curve")
    )
    replay.expect("extension_field.curve.a", curve.get("a"), 0)
    replay.expect("extension_field.curve.b", curve.get("b"), 2)
    replay.expect(
        "extension_field.curve.discriminant_nonzero",
        curve.get("discriminant_nonzero"),
        (-16 * 27 * 2**2) % 5 != 0,
    )
    lifts = []
    for x in (1, 4):
        rhs = (x**3 + 2) % 5
        lifts.append(
            {
                "rhs": rhs,
                "x": x,
                "y_roots": [
                    y for y in range(5) if y * y % 5 == rhs
                ],
            }
        )
    replay.expect(
        "extension_field.curve.liftability",
        curve.get("liftability"),
        lifts,
    )
    replay.expect(
        "extension_field.curve.first_input_nonlift",
        lifts[0]["y_roots"],
        [],
    )

    slice_record = replay.require_dict(
        "extension_field.s3_slice", witness.get("s3_slice")
    )
    coefficients = s3_coefficients(5, 1, 4, b=2)
    roots = [
        value for value in range(5) if evaluate(coefficients, value, 5) == 0
    ]
    discriminant = (
        coefficients[1] ** 2
        - 4 * coefficients[0] * coefficients[2]
    ) % 5
    matrix = sylvester(coefficients, coefficients)
    resultant = determinant_laplace(matrix) % 5
    replay.expect(
        "extension_field.s3.inputs",
        slice_record.get("inputs"),
        [1, 4],
    )
    replay.expect(
        "extension_field.s3.s4_coordinates",
        slice_record.get("s4_coordinates"),
        [1, 4, 1, 4],
    )
    replay.expect(
        "extension_field.s3.coefficients",
        slice_record.get("coefficients_z2_z1_z0"),
        coefficients,
    )
    replay.expect(
        "extension_field.s3.coefficients.exact",
        coefficients,
        [4, 2, 1],
    )
    replay.expect(
        "extension_field.s3.discriminant",
        slice_record.get("discriminant"),
        discriminant,
    )
    replay.expect(
        "extension_field.s3.quadratic_residues",
        slice_record.get("quadratic_residues"),
        [0, 1, 4],
    )
    replay.expect(
        "extension_field.s3.base_field_roots",
        slice_record.get("base_field_roots"),
        roots,
    )
    replay.expect("extension_field.s3.no_base_root", roots, [])
    replay.expect(
        "extension_field.s3.sylvester_matrix",
        slice_record.get("sylvester_matrix"),
        matrix,
    )
    replay.expect(
        "extension_field.s3.self_resultant",
        slice_record.get("fixed_size_self_resultant"),
        resultant,
    )
    replay.expect("extension_field.s3.self_resultant.zero", resultant, 0)


def check_control_extension_fiber(
    document: dict[str, Any], replay: Replay
) -> None:
    witness = replay.require_dict(
        "control_field_extension_fiber_witness",
        document.get("control_field_extension_fiber_witness"),
    )
    membership = replay.require_dict(
        "control_extension.field_and_membership",
        witness.get("field_and_membership"),
    )
    replay.expect("control_extension.p", membership.get("p"), EXPECTED_CONTROL_P)
    replay.expect("control_extension.D", membership.get("D"), EXPECTED_D)
    leaf_x = [1, EXPECTED_CONTROL_P - 1, 1, EXPECTED_CONTROL_P - 1]
    leaf_x.extend([EXPECTED_BASE[0]] * 12)
    replay.expect(
        "control_extension.leaf_x_coordinates",
        membership.get("leaf_x_coordinates"),
        leaf_x,
    )
    replay.expect("control_extension.leaf_count", len(leaf_x), EXPECTED_M)
    for index, x in enumerate(leaf_x):
        replay.expect(
            f"control_extension.membership.leaf_{index}",
            pow(x, EXPECTED_D, EXPECTED_CONTROL_P),
            1,
        )

    direct = replay.require_dict(
        "control_extension.direct_extension_relation",
        witness.get("direct_extension_relation"),
    )
    replay.expect(
        "control_extension.target_scalar",
        direct.get("target_scalar"),
        12,
    )
    target = record_to_point(
        "control_extension.target_point",
        direct.get("target_point"),
        replay,
    )
    replay.expect(
        "control_extension.target",
        target,
        multiply(12, EXPECTED_BASE, EXPECTED_CONTROL_P),
    )
    if target is not None:
        replay.expect(
            "control_extension.target_x",
            membership.get("target_x"),
            target[0],
        )
        replay.expect(
            "control_extension.target_membership",
            pow(target[0], EXPECTED_D, EXPECTED_CONTROL_P),
            1,
        )

    liftability = replay.require_list(
        "control_extension.liftability",
        witness.get("liftability"),
    )
    expected_lifts = [
        {
            "legendre_symbol": -1,
            "rhs": 8,
            "status": "extension_only",
            "x": 1,
        },
        {
            "legendre_symbol": 1,
            "rhs": 6,
            "status": "base_field_lift",
            "x": EXPECTED_CONTROL_P - 1,
            "y_roots": [163_761, 400_762],
        },
    ]
    replay.expect(
        "control_extension.liftability.records",
        liftability,
        expected_lifts,
    )
    replay.expect(
        "control_extension.x1_rhs_legendre",
        pow(8, (EXPECTED_CONTROL_P - 1) // 2, EXPECTED_CONTROL_P),
        EXPECTED_CONTROL_P - 1,
    )
    replay.expect(
        "control_extension.minus_one_rhs_legendre",
        pow(6, (EXPECTED_CONTROL_P - 1) // 2, EXPECTED_CONTROL_P),
        1,
    )
    for y in (163_761, 400_762):
        replay.expect(
            f"control_extension.minus_one_lift_{y}",
            y * y % EXPECTED_CONTROL_P,
            6,
        )

    first_slice = replay.require_dict(
        "control_extension.first_affine_slice",
        witness.get("first_affine_slice"),
    )
    coefficients = s3_coefficients(
        EXPECTED_CONTROL_P, 1, EXPECTED_CONTROL_P - 1
    )
    discriminant = (
        coefficients[1] ** 2
        - 4 * coefficients[0] * coefficients[2]
    ) % EXPECTED_CONTROL_P
    matrix = sylvester(coefficients, coefficients)
    resultant = determinant_laplace(matrix) % EXPECTED_CONTROL_P
    replay.expect(
        "control_extension.first_slice.inputs",
        first_slice.get("inputs"),
        [1, EXPECTED_CONTROL_P - 1],
    )
    replay.expect(
        "control_extension.first_slice.coefficients",
        first_slice.get("coefficients_z2_z1_z0"),
        coefficients,
    )
    replay.expect(
        "control_extension.first_slice.coefficients.exact",
        coefficients,
        [4, EXPECTED_CONTROL_P - 28, 1],
    )
    replay.expect(
        "control_extension.first_slice.discriminant",
        first_slice.get("discriminant"),
        discriminant,
    )
    replay.expect(
        "control_extension.first_slice.discriminant.exact",
        discriminant,
        768,
    )
    replay.expect(
        "control_extension.first_slice.nonsquare",
        pow(
            discriminant,
            (EXPECTED_CONTROL_P - 1) // 2,
            EXPECTED_CONTROL_P,
        ),
        EXPECTED_CONTROL_P - 1,
    )
    replay.expect(
        "control_extension.first_slice.base_field_roots",
        first_slice.get("base_field_roots"),
        [],
    )
    replay.expect(
        "control_extension.first_slice.sylvester",
        first_slice.get("sylvester_matrix"),
        matrix,
    )
    replay.expect(
        "control_extension.first_slice.resultant",
        first_slice.get("fixed_size_self_resultant"),
        resultant,
    )
    replay.expect("control_extension.first_slice.resultant.zero", resultant, 0)
    scope = witness.get("scope")
    if not isinstance(scope, str) or (
        "Recovery rejects this tuple" not in scope
        or "not an S17 evaluation" not in scope
    ):
        replay.failures.append(
            "control extension witness lacks recovery and S17 scope"
        )


def check_contracts(document: dict[str, Any], replay: Replay) -> None:
    presentation = replay.require_dict(
        "m16_presentation_contract",
        document.get("m16_presentation_contract"),
    )
    direct = replay.require_dict(
        "m16_presentation_contract.direct_relation",
        presentation.get("direct_relation"),
    )
    replay.expect(
        "m16.direct.polynomial",
        direct.get("polynomial"),
        "S_17(x_1,...,x_16,x_target)",
    )
    replay.expect(
        "m16.direct.polynomial_materialized",
        direct.get("polynomial_materialized"),
        False,
    )
    recursive = replay.require_dict(
        "m16_presentation_contract.recursive_affine_left_fold",
        presentation.get("recursive_affine_left_fold"),
    )
    internals = [f"u_{index}" for index in range(2, 16)]
    equations = ["S3(x_1, x_2, u_2) = 0"]
    equations.extend(
        f"S3(u_{index - 1}, x_{index}, u_{index}) = 0"
        for index in range(3, 16)
    )
    equations.append("S3(u_15, x_16, x_target) = 0")
    replay.expect(
        "m16.recursive.internal_variables",
        recursive.get("internal_variables"),
        internals,
    )
    replay.expect(
        "m16.recursive.internal_variable_count",
        recursive.get("internal_variable_count"),
        14,
    )
    replay.expect(
        "m16.recursive.equations",
        recursive.get("equations"),
        equations,
    )
    replay.expect(
        "m16.recursive.equation_count",
        recursive.get("equation_count"),
        15,
    )
    membership = replay.require_dict(
        "m16_presentation_contract.membership",
        presentation.get("membership"),
    )
    replay.expect(
        "m16.membership.artifact",
        membership.get("artifact"),
        EXPECTED_M16_DESK_PATH,
    )
    replay.expect(
        "m16.membership.artifact_sha256",
        membership.get("artifact_sha256"),
        EXPECTED_M16_DESK_SHA256,
    )
    replay.expect(
        "m16.membership.gates",
        membership.get("circuit_gate_count_per_coordinate"),
        24,
    )

    bridge = replay.require_dict(
        "conditional_bridge", document.get("conditional_bridge")
    )
    replay.expect(
        "conditional_bridge.status",
        bridge.get("status"),
        "exact_only_after_nonidentity_localization",
    )
    domain = replay.require_list(
        "conditional_bridge.affine_left_fold_exact_domain",
        bridge.get("affine_left_fold_exact_domain"),
    )
    if len(domain) != 6 or not any("not the identity" in item for item in domain):
        replay.failures.append(
            "conditional bridge does not bind the nonidentity prefix domain"
        )
    if not any("for the fixed leaf order" in item for item in domain):
        replay.failures.append(
            "conditional bridge must bind the labeled leaf order"
        )
    missing = bridge.get("missing_global_stratum")
    if not isinstance(missing, str) or (
        "no affine x-coordinate" not in missing
        or "not globally complete" not in missing
    ):
        replay.failures.append(
            "conditional bridge must expose the identity-prefix obstruction"
        )

    local = replay.require_dict(
        "local_s3_semantics", document.get("local_s3_semantics")
    )
    repeated = replay.require_dict(
        "local_s3_semantics.repeated_inputs",
        local.get("repeated_inputs"),
    )
    replay.expect(
        "local_s3.repeated.specialization",
        repeated.get("specialization"),
        "S3(x,x,z) = -4*y^2 * (z - x(2P))",
    )
    replay.expect(
        "local_s3.repeated.localization",
        repeated.get("localization"),
        "4*y^2 != 0",
    )
    identity = replay.require_dict(
        "local_s3_semantics.identity_branch",
        local.get("identity_branch"),
    )
    replay.expect(
        "local_s3.identity.affine_parent",
        identity.get("affine_parent"),
        None,
    )

    projective = replay.require_dict(
        "projective_completion_candidate",
        document.get("projective_completion_candidate"),
    )
    replay.expect(
        "projective.status",
        projective.get("status"),
        "next_task_requires_independent_proof",
    )
    replay.expect(
        "projective.homogeneous_polynomial",
        projective.get("homogeneous_polynomial"),
        (
            "X1^2*X2^2*Z3^2 + X1^2*Z2^2*X3^2 + "
            "Z1^2*X2^2*X3^2 - 2*X1^2*X2*Z2*X3*Z3 - "
            "2*X1*Z1*X2^2*X3*Z3 - "
            "2*X1*Z1*X2*Z2*X3^2 - "
            "28*(X1*Z1*Z2^2*Z3^2 + "
            "Z1^2*X2*Z2*Z3^2 + Z1^2*Z2^2*X3*Z3)"
        ),
    )
    kummer = replay.require_dict(
        "projective.kummer_coordinate",
        projective.get("kummer_coordinate"),
    )
    replay.expect("projective.kummer.identity", kummer.get("identity"), "[1:0]")
    replay.expect(
        "projective.kummer.affine_point",
        kummer.get("affine_point"),
        "[x(P):1]",
    )
    replay.expect(
        "projective.repeated_slice",
        projective.get("repeated_input_homogeneous_slice"),
        (
            "S3^h(x,x;U,V) = V * "
            "(-4*y^2*U + (x^4 - 56*x)*V)"
        ),
    )
    saturation = projective.get("saturation_policy")
    if not isinstance(saturation, str) or (
        "do not saturate by coordinate differences" not in saturation
    ):
        replay.failures.append(
            "projective candidate must preserve tangent and duplicate strata"
        )

    affine_terms: dict[tuple[int, int, int], int] = {}
    one_infinity_terms: dict[tuple[int, int, int, int], int] = {}
    two_infinity_terms: dict[tuple[int, int], int] = {}
    repeated_terms: dict[tuple[int, int, int], int] = {}
    for exponents, coefficient in HOMOGENEOUS_S3_TERMS.items():
        affine_key = (exponents[0], exponents[2], exponents[4])
        affine_terms[affine_key] = (
            affine_terms.get(affine_key, 0) + coefficient
        )
        if exponents[5] == 0:
            one_key = (
                exponents[0],
                exponents[1],
                exponents[2],
                exponents[3],
            )
            one_infinity_terms[one_key] = (
                one_infinity_terms.get(one_key, 0) + coefficient
            )
        if exponents[3] == 0 and exponents[5] == 0:
            two_key = (exponents[0], exponents[1])
            two_infinity_terms[two_key] = (
                two_infinity_terms.get(two_key, 0) + coefficient
            )
        repeated_key = (
            exponents[0] + exponents[2],
            exponents[4],
            exponents[5],
        )
        repeated_terms[repeated_key] = (
            repeated_terms.get(repeated_key, 0) + coefficient
        )
    affine_terms = {
        key: value for key, value in affine_terms.items() if value
    }
    one_infinity_terms = {
        key: value for key, value in one_infinity_terms.items() if value
    }
    two_infinity_terms = {
        key: value for key, value in two_infinity_terms.items() if value
    }
    repeated_terms = {
        key: value for key, value in repeated_terms.items() if value
    }
    replay.expect(
        "projective.integer_coefficients.affine_chart",
        affine_terms,
        {
            (2, 2, 0): 1,
            (2, 0, 2): 1,
            (0, 2, 2): 1,
            (2, 1, 1): -2,
            (1, 2, 1): -2,
            (1, 1, 2): -2,
            (1, 0, 0): -28,
            (0, 1, 0): -28,
            (0, 0, 1): -28,
        },
    )
    replay.expect(
        "projective.integer_coefficients.one_infinity",
        one_infinity_terms,
        {
            (2, 0, 0, 2): 1,
            (0, 2, 2, 0): 1,
            (1, 1, 1, 1): -2,
        },
    )
    replay.expect(
        "projective.integer_coefficients.two_infinities",
        two_infinity_terms,
        {(0, 2): 1},
    )
    replay.expect(
        "projective.integer_coefficients.repeated_input",
        repeated_terms,
        {
            (3, 1, 1): -4,
            (0, 1, 1): -28,
            (4, 0, 2): 1,
            (1, 0, 2): -56,
        },
    )

    for x1 in range(13):
        for x2 in range(13):
            coefficients = s3_coefficients(13, x1, x2)
            for x3 in range(13):
                replay.expect(
                    f"projective.affine_chart.{x1}.{x2}.{x3}",
                    s3_homogeneous(13, x1, 1, x2, 1, x3, 1),
                    evaluate(coefficients, x3, 13),
                )
    for x1 in range(13):
        for z1 in range(13):
            for x2 in range(13):
                for z2 in range(13):
                    replay.expect(
                        f"projective.one_infinity.{x1}.{z1}.{x2}.{z2}",
                        s3_homogeneous(
                            13, x1, z1, x2, z2, 1, 0
                        ),
                        (x1 * z2 - x2 * z1) ** 2 % 13,
                    )
    for x1 in range(13):
        for z1 in range(13):
            replay.expect(
                f"projective.two_infinities.{x1}.{z1}",
                s3_homogeneous(13, x1, z1, 1, 0, 1, 0),
                z1 * z1 % 13,
            )
    for x in range(13):
        for y in range(13):
            if (y * y - x**3 - 7) % 13 != 0:
                continue
            for u in range(13):
                for v in range(13):
                    replay.expect(
                        f"projective.repeated.{x}.{y}.{u}.{v}",
                        s3_homogeneous(13, x, 1, x, 1, u, v),
                        (
                            v
                            * (
                                -4 * y * y * u
                                + (x**4 - 56 * x) * v
                            )
                        )
                        % 13,
                    )

    recovery = replay.require_dict(
        "recovery_contract", document.get("recovery_contract")
    )
    signs = replay.require_dict(
        "recovery_contract.direct_sign_search",
        recovery.get("direct_sign_search"),
    )
    replay.expect("recovery.raw_assignments", signs.get("raw_assignments"), 1 << 16)
    replay.expect(
        "recovery.relative_classes", signs.get("relative_classes"), 1 << 15
    )
    replay.expect(
        "recovery.meet_in_the_middle",
        signs.get("meet_in_the_middle_list_sizes"),
        [1 << 7, 1 << 8],
    )
    acceptance = replay.require_list(
        "recovery_contract.acceptance", recovery.get("acceptance")
    )
    for phrase in (
        "combine duplicate signed points before emitting a relation row",
        "canonicalize coordinate permutations so they do not count as independent relations",
        "verify the full elliptic-curve relation and target coefficient exactly",
    ):
        if phrase not in acceptance:
            replay.failures.append(
                f"recovery acceptance lacks {phrase!r}"
            )
    glv_items = [item for item in acceptance if "lambda^j" in item]
    if len(glv_items) != 1:
        replay.failures.append(
            "recovery contract lacks one exact GLV coefficient rule"
        )
    canonical_row = replay.require_dict(
        "recovery_contract.canonical_relation_row",
        recovery.get("canonical_relation_row"),
    )
    replay.expect(
        "recovery.canonical_row.status",
        canonical_row.get("status"),
        "required_before_rank_accounting",
    )
    replay.expect(
        "recovery.canonical_row.steps",
        canonical_row.get("steps"),
        [
            "ordered lifted leaf tuple",
            "exact signed point tuple with target",
            "duplicate-aggregated point row",
            "GLV-normalized sparse coefficient row",
            "exact curve re-verification",
        ],
    )
    target_normalization = canonical_row.get("target_normalization")
    if not isinstance(target_normalization, str) or (
        "target coefficient to -1" not in target_normalization
        or "signed leaf sum equals R" not in target_normalization
    ):
        replay.failures.append(
            "canonical relation row lacks exact target normalization"
        )
    final_verification = canonical_row.get("final_verification")
    if not isinstance(final_verification, str) or (
        "exact group sum is the identity" not in final_verification
    ):
        replay.failures.append(
            "canonical relation row lacks exact post-normalization verification"
        )

    glv = replay.require_dict(
        "recovery_contract.glv_normalization",
        recovery.get("glv_normalization"),
    )
    replay.expect(
        "recovery.glv.eigenvalue_theorem",
        glv.get("eigenvalue_theorem"),
        "Ecdlp.Curve.secp256k1_glvPoint_eq_lam_on_zmultiples",
    )
    replay.expect(
        "recovery.glv.subgroup_eigenvalue_path",
        glv.get("subgroup_eigenvalue_path"),
        "Ecdlp/Proved/GlvSubgroupEigenvalue.lean",
    )
    replay.expect(
        "recovery.glv.orbit_path",
        glv.get("orbit_path"),
        "Ecdlp/Proved/GlvOrbit.lean",
    )
    replay.expect(
        "recovery.glv.full_group_membership_path",
        glv.get("full_group_membership_path"),
        "Ecdlp/Proved/CurveFullGroup.lean",
    )
    replay.expect(
        "recovery.glv.full_group_membership_theorem",
        glv.get("full_group_membership_theorem"),
        "Ecdlp.Curve.secp256k1_mem_zmultiples",
    )
    replay.expect(
        "recovery.glv.status",
        glv.get("status"),
        "future_requirement_not_replayed",
    )
    coefficient_rule = glv.get("coefficient_rule")
    if not isinstance(coefficient_rule, str) or (
        "epsilon*eta*lambda^j modulo n" not in coefficient_rule
    ):
        replay.failures.append("GLV normalization lacks coefficient rule")
    representative_rule = glv.get("representative_rule")
    if not isinstance(representative_rule, str) or (
        "modulo point sign" not in representative_rule
        or "Q=eta*phi^j(P0)" not in representative_rule
    ):
        replay.failures.append(
            "GLV normalization lacks point-sign transport"
        )

    dynamic_program = replay.require_dict(
        "recovery_contract.ordered_tree_dynamic_program",
        recovery.get("ordered_tree_dynamic_program"),
    )
    replay.expect(
        "recovery.dynamic_program.state_bound",
        dynamic_program.get("state_bound_per_supplied_x"),
        2,
    )
    for field, phrase in (
        ("leaf_states", "{P_i,-P_i}"),
        ("parent_transition", "x(A+B) equals"),
        ("identity_state", "non-affine stratum"),
        ("backpointers", "backpointers"),
        ("root_acceptance", "R or -R"),
    ):
        value = dynamic_program.get(field)
        if not isinstance(value, str) or phrase not in value:
            replay.failures.append(
                f"ordered tree dynamic program lacks {field!r}"
            )

    permutations = replay.require_dict(
        "recovery_contract.permutation_accounting",
        recovery.get("permutation_accounting"),
    )
    replay.expect(
        "recovery.permutations.direct_orbit_count",
        permutations.get("direct_coordinate_orbit_count"),
        "16! / product_x multiplicity(x)!",
    )
    replay.expect(
        "recovery.permutations.levels",
        permutations.get("levels"),
        [
            "ordered leaf tuple and fixed tree topology",
            "sorted coordinate multiset",
            "normalized sparse GLV row",
        ],
    )
    recursive_warning = permutations.get("recursive_warning")
    if not isinstance(recursive_warning, str) or (
        "topology dependent" not in recursive_warning
        or "must be replayed" not in recursive_warning
    ):
        replay.failures.append(
            "permutation accounting does not bind topology dependence"
        )

    audit = replay.require_dict(
        "recovery_contract.permutation_recovery_audit",
        recovery.get("permutation_recovery_audit"),
    )
    replayed = replay_recovery_preimages()
    replay.expect(
        "recovery.audit.unique_orderings",
        audit.get("unique_orderings"),
        replayed["unique_orderings"],
    )
    replay.expect(
        "recovery.audit.unique_orderings.exact",
        replayed["unique_orderings"],
        math.factorial(16) // (math.factorial(14) * math.factorial(2)),
    )
    replay.expect(
        "recovery.audit.direct_preimages",
        audit.get("direct_preimages"),
        len(replayed["records"]),
    )
    replay.expect(
        "recovery.audit.direct_preimages.exact",
        len(replayed["records"]),
        240,
    )
    derived_rows: set[tuple[int, int]] = set()
    for record in replayed["records"]:
        repeated_positions = set(
            record["repeated_positions_zero_based"]
        )
        mask = record["sign_mask_tail_15"]
        signs = [1] + [
            1 if mask & (1 << (index - 1)) else -1
            for index in range(1, EXPECTED_M)
        ]
        orientation = record["target_orientation"]
        derived_rows.add(
            (
                orientation
                * sum(
                    signs[index]
                    for index in range(EXPECTED_M)
                    if index not in repeated_positions
                ),
                orientation
                * sum(
                    signs[index] for index in repeated_positions
                ),
            )
        )
    replay.expect(
        "recovery.audit.derived_rows",
        derived_rows,
        {(14, 0)},
    )
    replay.expect(
        "recovery.audit.derived_point_basis_coefficients",
        audit.get("derived_point_basis_coefficients"),
        {"base_P": 14, "repeated_50P": 0},
    )
    replay.expect(
        "recovery.audit.normalized_row_preimages",
        audit.get("normalized_row_preimages"),
        len(replayed["records"]),
    )
    replay.expect(
        "recovery.audit.affine_admissible_preimages",
        audit.get("affine_admissible_preimages"),
        len(replayed["admissible"]),
    )
    replay.expect(
        "recovery.audit.affine_admissible_preimages.exact",
        len(replayed["admissible"]),
        238,
    )
    replay.expect(
        "recovery.audit.identity_blocked_preimages",
        audit.get("identity_blocked_preimages"),
        len(replayed["blocked"]),
    )
    replay.expect(
        "recovery.audit.identity_blocked_preimages.exact",
        len(replayed["blocked"]),
        2,
    )
    replay.expect(
        "recovery.audit.blocked_records",
        audit.get("blocked_records"),
        replayed["blocked"],
    )
    replay.expect(
        "recovery.audit.blocked_ranks",
        sorted(
            {
                record["permutation_rank"]
                for record in replayed["blocked"]
            }
        ),
        [0],
    )
    replay.expect(
        "recovery.audit.blocked_prefixes",
        sorted(
            {
                tuple(record["identity_prefix_sizes"])
                for record in replayed["blocked"]
            }
        ),
        [(2,)],
    )
    for field, expected in (
        ("accepted_record_sha256", replayed["accepted_record_sha256"]),
        (
            "affine_admissible_record_sha256",
            replayed["affine_admissible_record_sha256"],
        ),
        ("per_rank_counts_sha256", replayed["per_rank_counts_sha256"]),
        ("normalized_row_sha256", replayed["row_sha256"]),
    ):
        replay.expect(f"recovery.audit.{field}", audit.get(field), expected)
    replay.expect(
        "recovery.audit.coordinate_multiset",
        audit.get("coordinate_multiset"),
        [
            {"multiplicity": 14, "scalar_on_P": 1},
            {"multiplicity": 2, "scalar_on_P": 50},
        ],
    )
    replay.expect(
        "recovery.audit.normalized_row",
        audit.get("normalized_row"),
        replayed["row"],
    )
    replay.expect(
        "recovery.audit.ordering_rank_definition",
        audit.get("ordering_rank_definition"),
        (
            "lexicographic combinations of the two zero-based positions "
            "occupied by repeated_50P"
        ),
    )
    replay.expect(
        "recovery.audit.relative_sign_convention",
        audit.get("relative_sign_convention"),
        (
            "the first leaf sign is +1; bit i-1 of sign_mask_tail_15 "
            "selects +1 for leaf i and 0 selects -1"
        ),
    )
    replay.expect(
        "recovery.audit.normalized_row.group_check",
        add(
            multiply(14, EXPECTED_BASE, EXPECTED_CONTROL_P),
            negate(EXPECTED_TARGET, EXPECTED_CONTROL_P),
            EXPECTED_CONTROL_P,
        ),
        None,
    )


def check_terminal(document: dict[str, Any], replay: Replay) -> None:
    terminal = replay.require_dict(
        "terminal_disposition", document.get("terminal_disposition")
    )
    expected = {
        "authorization": "none",
        "barrier_effect": "narrowed_open",
        "cell_transition": "open_to_open",
        "cost_quantity_transition": "partial_to_partial",
        "hypothesis_effect": "none",
        "retention_disposition": "zero_retention_success",
        "route_effect": "none",
        "scientific_disposition": "scoped_blocker",
        "source_independence": "not_established",
    }
    for field, value in expected.items():
        replay.expect(f"terminal_disposition.{field}", terminal.get(field), value)
    replay.expect(
        "unresolved_fields",
        document.get("unresolved_fields"),
        [
            "target-field occurrence and frequency of identity-prefix strata",
            "projective or explicitly stratified recursive presentation",
            "distinct-coordinate localization and its relation-yield effect",
            "complete liftability and exceptional-fiber classification",
            "duplicate, permutation, GLV-orbit, and rank multiplicities",
            "direct S17 semantics and recursive projection on every remaining stratum",
            "solving degree, fill-in, preprocessing, sparse linear algebra, and total cost",
        ],
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, default=HERE / "artifact.json")
    parser.add_argument(
        "--hash-file", type=Path, default=HERE / "artifact.sha256"
    )
    args = parser.parse_args()

    replay = Replay()
    try:
        artifact_bytes = args.artifact.read_bytes()
        document = json.loads(artifact_bytes)
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError) as error:
        print(f"ERROR: artifact unreadable: {error}", file=sys.stderr)
        return 1
    if not isinstance(document, dict):
        print("ERROR: artifact root must be an object", file=sys.stderr)
        return 1
    if artifact_bytes != canonical_bytes(document):
        replay.failures.append("artifact.json is not canonical JSON")
    check_hash(artifact_bytes, args.hash_file, replay)
    check_metadata(document, replay)
    check_source_scope(document, replay)
    check_control_counterexample(document, replay)
    check_small_boundary(document, replay)
    check_extension_membership_witness(document, replay)
    check_control_extension_fiber(document, replay)
    check_contracts(document, replay)
    check_terminal(document, replay)

    if replay.failures:
        for failure in replay.failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    print("independent M16 semantic bridge replay passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
