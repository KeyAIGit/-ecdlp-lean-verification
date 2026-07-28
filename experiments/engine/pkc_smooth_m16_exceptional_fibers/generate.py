#!/usr/bin/env python3
"""Generate the deterministic TASK-017 exceptional-fiber certificate.

The producer uses only exact finite-field and elliptic-curve arithmetic.  It
freezes the homogeneous projective S3 left fold, replays every local
projective transition over two small fields, executes supplied-coordinate
recovery on the 120 control orderings, and checks a fixed secp256k1 GLV row.
The direct S17 polynomial is deliberately not defined or materialized here.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ARTIFACT_ID = "PKC-SMOOTH-M16-EXCEPTIONAL-FIBERS-001"
SCHEMA_VERSION = "1.0"
M = 16
D = 564_522
FACTOR_CHAIN = (2, 3, 7, 13_441)

PRIOR_ARTIFACT = (
    "experiments/engine/pkc_smooth_m16_semantic_bridge/artifact.json"
)
PRIOR_SHA256 = (
    "963eea60097807ae0aa66a5d881b0c34bf0497ade53ed4d37d38861a73887c19"
)
PRIMARY_CLAIM_EXTRACT = (
    "data/source_claim_extracts/petit_kosters_messeng2016.json"
)
PRIMARY_CLAIM_EXTRACT_SHA256 = (
    "f8839553f6935ed5cd331369cc13d91124373750c757b28eeca3ee773835f14f"
)
SOURCE_CLAIM_IDS = (
    "SC-PKC-SMOOTH-SUBGROUP",
    "SC-SEMAEV-RELATION-SEMANTICS",
    "SC-SECP-NO-TWO-TORSION",
    "SC-GLV-ENDOMORPHISM",
    "SC-GLV-ENDOMORPHISM-NONTRIVIAL",
    "SC-PKC-M16-SEMANTIC-BRIDGE-RESULT",
)
EXCLUDED_CHARACTERISTICS = (2, 3, 7)

CONTROL_P = D + 1
CONTROL_A = 0
CONTROL_B = 7
CONTROL_CURVE_ORDER = 564_469
CONTROL_CURVE_ORDER_FACTORS = (163, 3_463)
CONTROL_SUBGROUP_ORDER = 3_463
CONTROL_COFACTOR = 163
CONTROL_SEED = (2, 100_588)
CONTROL_BASE_SCALAR = 1
CONTROL_REPEATED_SCALAR = 50
CONTROL_TARGET_SCALAR = 14

SECP_P = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16
)
SECP_N = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16
)
SECP_LAMBDA = int(
    "5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72",
    16,
)
SECP_BETA = int(
    "7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE",
    16,
)

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
ARTIFACT_PATH = HERE / "artifact.json"
HASH_PATH = HERE / "artifact.sha256"

Point = tuple[int, int] | None
Projective = tuple[int, int]


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def is_prime_trial(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    divisor = 3
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 2
    return True


def legendre_symbol(value: int, prime: int) -> int:
    residue = value % prime
    if residue == 0:
        return 0
    result = pow(residue, (prime - 1) // 2, prime)
    if result == 1:
        return 1
    if result == prime - 1:
        return -1
    raise AssertionError("Euler criterion returned an invalid value")


def curve_rhs(x: int, prime: int, a: int = 0, b: int = 7) -> int:
    return (x**3 + a * x + b) % prime


def curve_discriminant(prime: int, a: int, b: int) -> int:
    return (-16 * (4 * a**3 + 27 * b**2)) % prime


def curve_order(prime: int, a: int, b: int) -> int:
    return prime + 1 + sum(
        legendre_symbol(curve_rhs(x, prime, a, b), prime)
        for x in range(prime)
    )


def on_curve(point: Point, prime: int, a: int = 0, b: int = 7) -> bool:
    if point is None:
        return True
    x, y = point
    return (y * y - curve_rhs(x, prime, a, b)) % prime == 0


def point_neg(point: Point, prime: int) -> Point:
    if point is None:
        return None
    return point[0], (-point[1]) % prime


def point_add(
    left: Point,
    right: Point,
    prime: int,
    a: int = 0,
    b: int = 7,
) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    if not on_curve(left, prime, a, b) or not on_curve(
        right, prime, a, b
    ):
        raise ValueError("point_add received an off-curve point")
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % prime == 0:
        return None
    if left == right:
        denominator = (2 * y1) % prime
        if denominator == 0:
            return None
        slope = (3 * x1 * x1 + a) * pow(
            denominator, prime - 2, prime
        )
    else:
        denominator = (x2 - x1) % prime
        slope = (y2 - y1) * pow(denominator, prime - 2, prime)
    slope %= prime
    x3 = (slope * slope - x1 - x2) % prime
    y3 = (slope * (x1 - x3) - y1) % prime
    result = (x3, y3)
    if not on_curve(result, prime, a, b):
        raise AssertionError("point addition left the curve")
    return result


def scalar_mul(
    scalar: int,
    point: Point,
    prime: int,
    a: int = 0,
    b: int = 7,
) -> Point:
    if scalar < 0:
        return scalar_mul(-scalar, point_neg(point, prime), prime, a, b)
    result: Point = None
    addend = point
    value = scalar
    while value:
        if value & 1:
            result = point_add(result, addend, prime, a, b)
        addend = point_add(addend, addend, prime, a, b)
        value >>= 1
    return result


def point_record(point: Point) -> dict[str, Any]:
    if point is None:
        return {"kind": "identity"}
    return {"kind": "affine", "x": point[0], "y": point[1]}


def q_record(q: Projective) -> dict[str, Any]:
    x, z = q
    if x == 0 and z == 0:
        return {"X": 0, "Z": 0, "kind": "invalid"}
    if z == 0:
        return {"X": 1, "Z": 0, "kind": "identity"}
    return {"X": x, "Z": 1, "kind": "finite", "x": x}


def kappa(point: Point) -> Projective:
    if point is None:
        return 1, 0
    return point[0], 1


def s3_coefficients(
    prime: int, a: int, b: int, x1: int, x2: int
) -> tuple[int, int, int]:
    """Return coefficients of z^2, z, 1 for affine S3."""
    return (
        (x1 - x2) ** 2 % prime,
        (
            -2
            * ((x1 + x2) * (x1 * x2 + a) + 2 * b)
        )
        % prime,
        ((x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)) % prime,
    )


def s3h_eval(
    q1: Projective,
    q2: Projective,
    q3: Projective,
    prime: int,
) -> int:
    x1, z1 = q1
    x2, z2 = q2
    x3, z3 = q3
    value = (
        x1**2 * x2**2 * z3**2
        + x1**2 * z2**2 * x3**2
        + z1**2 * x2**2 * x3**2
        - 2 * x1**2 * x2 * z2 * x3 * z3
        - 2 * x1 * z1 * x2**2 * x3 * z3
        - 2 * x1 * z1 * x2 * z2 * x3**2
        - 28
        * (
            x1 * z1 * z2**2 * z3**2
            + z1**2 * x2 * z2 * z3**2
            + z1**2 * z2**2 * x3 * z3
        )
    )
    return value % prime


def output_binary_coefficients(
    q1: Projective, q2: Projective, prime: int
) -> tuple[int, int, int]:
    """Return A,B,C for H(q1,q2,[U:V])=A U^2+B UV+C V^2."""
    coefficient_u2 = s3h_eval(q1, q2, (1, 0), prime)
    coefficient_v2 = s3h_eval(q1, q2, (0, 1), prime)
    at_one_one = s3h_eval(q1, q2, (1, 1), prime)
    coefficient_uv = (
        at_one_one - coefficient_u2 - coefficient_v2
    ) % prime
    return coefficient_u2, coefficient_uv, coefficient_v2


def projective_roots_with_multiplicity(
    coefficients: tuple[int, int, int], prime: int
) -> list[dict[str, Any]]:
    coefficient_u2, coefficient_uv, coefficient_v2 = coefficients
    roots: list[dict[str, Any]] = []
    for value in range(prime):
        evaluation = (
            coefficient_u2 * value * value
            + coefficient_uv * value
            + coefficient_v2
        ) % prime
        if evaluation == 0:
            derivative = (
                2 * coefficient_u2 * value + coefficient_uv
            ) % prime
            roots.append(
                {
                    "coordinate": q_record((value, 1)),
                    "multiplicity": 2 if derivative == 0 else 1,
                }
            )
    if coefficient_u2 == 0:
        roots.append(
            {
                "coordinate": q_record((1, 0)),
                "multiplicity": 2 if coefficient_uv == 0 else 1,
            }
        )
    return roots


def transition_type(
    left: Projective, right: Projective, prime: int
) -> str:
    if left == (0, 0) or right == (0, 0):
        return "invalid_projective_input"
    if left[1] == 0 or right[1] == 0:
        return "identity_input_duplicate"
    x1 = left[0]
    x2 = right[0]
    if x1 == x2:
        if curve_rhs(x1, prime) == 0:
            return "repeated_two_torsion_duplicate"
        return "repeated_tangent"
    product = curve_rhs(x1, prime) * curve_rhs(x2, prime)
    character = legendre_symbol(product, prime)
    if character == 0:
        return "distinct_two_torsion_duplicate"
    if character == 1:
        return "distinct_rational_split"
    return "distinct_extension_only"


def leaf_type(q: Projective, prime: int) -> str:
    if q == (0, 0):
        return "invalid_projective"
    if q[1] == 0:
        return "identity"
    character = legendre_symbol(curve_rhs(q[0], prime), prime)
    if character == 1:
        return "finite_base_pair"
    if character == -1:
        return "finite_extension_pair"
    return "finite_rational_two_torsion"


def named_transition(
    prime: int, left: Projective, right: Projective
) -> dict[str, Any]:
    coefficients = output_binary_coefficients(left, right, prime)
    return {
        "input": [q_record(left), q_record(right)],
        "type": transition_type(left, right, prime),
        "output_binary_coefficients_U2_UV_V2": list(coefficients),
        "fp_roots": projective_roots_with_multiplicity(
            coefficients, prime
        ),
    }


def exhaustive_small_field_replay(prime: int) -> dict[str, Any]:
    if prime in EXCLUDED_CHARACTERISTICS:
        raise ValueError(
            "small-field replay requires char(k) not in {2,3,7}"
        )
    if curve_discriminant(prime, 0, 7) == 0:
        raise ValueError("small-field replay requires a nonsingular curve")
    coordinates = [(1, 0), *[(x, 1) for x in range(prime)]]
    leaf_records = [
        {
            "coordinate": q_record(q),
            "rhs": None if q[1] == 0 else curve_rhs(q[0], prime),
            "type": leaf_type(q, prime),
        }
        for q in coordinates
    ]
    transition_records: list[dict[str, Any]] = []
    type_counts: Counter[str] = Counter()
    root_profile: Counter[str] = Counter()
    for left in coordinates:
        for right in coordinates:
            kind = transition_type(left, right, prime)
            coefficients = output_binary_coefficients(left, right, prime)
            roots = projective_roots_with_multiplicity(coefficients, prime)
            type_counts[kind] += 1
            profile_key = (
                f"{len(roots)}_fp_roots_"
                f"{sum(root['multiplicity'] for root in roots)}_multiplicity"
            )
            root_profile[profile_key] += 1
            transition_records.append(
                {
                    "left": q_record(left),
                    "right": q_record(right),
                    "type": kind,
                    "coefficients": list(coefficients),
                    "roots": roots,
                }
            )

            if left[1] == 0 or right[1] == 0:
                other = right if left[1] == 0 else left
                if roots != [
                    {
                        "coordinate": q_record(other),
                        "multiplicity": 2,
                    }
                ]:
                    raise AssertionError("identity-input formula failed")
            elif left[0] == right[0]:
                x = left[0]
                for u, v in coordinates:
                    expected = (
                        v
                        * (
                            -4 * curve_rhs(x, prime) * u
                            + (x**4 - 56 * x) * v
                        )
                    ) % prime
                    if s3h_eval(left, right, (u, v), prime) != expected:
                        raise AssertionError("repeated-input formula failed")
            else:
                a = left[0]
                b = right[0]
                discriminant = (
                    coefficients[1] ** 2
                    - 4 * coefficients[0] * coefficients[2]
                ) % prime
                expected_discriminant = (
                    16
                    * curve_rhs(a, prime)
                    * curve_rhs(b, prime)
                ) % prime
                if discriminant != expected_discriminant:
                    raise AssertionError("S3 discriminant identity failed")

            for output in coordinates:
                if left[1] == 0:
                    expected = (
                        right[0] * output[1]
                        - right[1] * output[0]
                    ) ** 2 % prime
                    if s3h_eval(left, right, output, prime) != expected:
                        raise AssertionError("left identity formula failed")
                if right[1] == 0:
                    expected = (
                        left[0] * output[1]
                        - left[1] * output[0]
                    ) ** 2 % prime
                    if s3h_eval(left, right, output, prime) != expected:
                        raise AssertionError("right identity formula failed")

    if sum(type_counts.values()) != (prime + 1) ** 2:
        raise AssertionError("small-field transition enumeration is incomplete")

    if prime == 13:
        examples = {
            "base_base_split": named_transition(
                prime, (7, 1), (8, 1)
            ),
            "twist_twist_split": named_transition(
                prime, (1, 1), (2, 1)
            ),
            "base_twist_extension_only": named_transition(
                prime, (7, 1), (1, 1)
            ),
            "base_repeated_tangent": named_transition(
                prime, (7, 1), (7, 1)
            ),
            "twist_repeated_tangent": named_transition(
                prime, (1, 1), (1, 1)
            ),
            "identity_input": named_transition(
                prime, (1, 0), (7, 1)
            ),
        }
    elif prime == 11:
        examples = {
            "repeated_two_torsion": named_transition(
                prime, (5, 1), (5, 1)
            ),
            "two_torsion_with_base_point": named_transition(
                prime, (5, 1), (2, 1)
            ),
            "two_torsion_with_twist_point": named_transition(
                prime, (5, 1), (1, 1)
            ),
            "ordinary_split": named_transition(
                prime, (2, 1), (3, 1)
            ),
            "ordinary_extension_only": named_transition(
                prime, (2, 1), (8, 1)
            ),
            "identity_identity": named_transition(
                prime, (1, 0), (1, 0)
            ),
        }
    else:
        examples = {}

    return {
        "field": f"F_{prime}",
        "p": prime,
        "curve": f"y^2 = x^3 + 7 over F_{prime}",
        "field_scope": (
            "char(F_p) not in {2,3,7}; curve discriminant is nonzero"
        ),
        "curve_discriminant_nonzero": curve_discriminant(
            prime, 0, 7
        )
        != 0,
        "projective_coordinate_count": prime + 1,
        "leaf_type_counts": dict(
            sorted(Counter(item["type"] for item in leaf_records).items())
        ),
        "leaf_records_sha256": digest(leaf_records),
        "ordered_transition_count": len(transition_records),
        "transition_type_counts": dict(sorted(type_counts.items())),
        "fp_root_profile": dict(sorted(root_profile.items())),
        "transition_records_sha256": digest(transition_records),
        "named_examples": examples,
        "checks": {
            "all_valid_input_pairs_classified_once": True,
            "identity_formula_all_coordinates": True,
            "repeated_formula_all_coordinates": True,
            "distinct_discriminant_formula_all_pairs": True,
            "root_multiplicity_replayed": True,
        },
    }


def scalar_kummer_token(
    scalar: int, base: Point, prime: int, order: int
) -> str | int:
    point = scalar_mul(scalar % order, base, prime)
    if point is None:
        return "O"
    return point[0]


def token_record(token: str | int) -> dict[str, Any]:
    if token == "O":
        return q_record((1, 0))
    if not isinstance(token, int):
        raise TypeError("finite Kummer token must be an integer")
    return q_record((token, 1))


def enumerate_control_preimages(base: Point) -> tuple[
    list[dict[str, Any]], list[dict[str, Any]]
]:
    ordering_records: list[dict[str, Any]] = []
    preimages: list[dict[str, Any]] = []
    for ordering_index, repeated_positions in enumerate(
        itertools.combinations(range(M), 2)
    ):
        leaf_scalars = [CONTROL_BASE_SCALAR] * M
        for position in repeated_positions:
            leaf_scalars[position] = CONTROL_REPEATED_SCALAR
        ordering_records.append(
            {
                "ordering_index": ordering_index,
                "repeated_positions_zero_based": list(repeated_positions),
                "leaf_scalars_on_P": leaf_scalars,
            }
        )

        right_by_sum: dict[int, list[int]] = defaultdict(list)
        for right_mask in range(1 << 8):
            right_sum = sum(
                (1 if (right_mask >> offset) & 1 else -1)
                * leaf_scalars[8 + offset]
                for offset in range(8)
            )
            right_by_sum[right_sum].append(right_mask)

        for left_mask in range(1 << 7):
            left_sum = leaf_scalars[0] + sum(
                (1 if (left_mask >> offset) & 1 else -1)
                * leaf_scalars[1 + offset]
                for offset in range(7)
            )
            for target_orientation in (-1, 1):
                required_right = (
                    target_orientation * CONTROL_TARGET_SCALAR - left_sum
                )
                for right_mask in right_by_sum.get(required_right, []):
                    tail_mask = left_mask | (right_mask << 7)
                    signs = [1] + [
                        1
                        if (tail_mask >> (index - 1)) & 1
                        else -1
                        for index in range(1, M)
                    ]
                    prefix_scalar = 0
                    internal_tokens: list[str | int] = []
                    identity_prefix_sizes: list[int] = []
                    for index, (sign, scalar) in enumerate(
                        zip(signs, leaf_scalars, strict=True), start=1
                    ):
                        prefix_scalar = (
                            prefix_scalar + sign * scalar
                        ) % CONTROL_SUBGROUP_ORDER
                        if 2 <= index <= M - 1:
                            token = scalar_kummer_token(
                                prefix_scalar,
                                base,
                                CONTROL_P,
                                CONTROL_SUBGROUP_ORDER,
                            )
                            internal_tokens.append(token)
                            if token == "O":
                                identity_prefix_sizes.append(index)
                    preimages.append(
                        {
                            "identity_prefix_sizes": identity_prefix_sizes,
                            "internal_tokens": internal_tokens,
                            "ordering_index": ordering_index,
                            "repeated_positions_zero_based": list(
                                repeated_positions
                            ),
                            "sign_mask_tail_15": tail_mask,
                            "target_orientation": target_orientation,
                        }
                    )

    preimages.sort(
        key=lambda item: (
            item["ordering_index"],
            item["sign_mask_tail_15"],
            item["target_orientation"],
        )
    )
    if len(ordering_records) != 120 or len(preimages) != 240:
        raise AssertionError("control ordering/preimage count mismatch")
    return ordering_records, preimages


def replay_supplied_internal_fiber(
    ordering: dict[str, Any],
    internal_tokens: list[str | int],
    base: Point,
) -> dict[str, Any]:
    leaf_scalars = ordering["leaf_scalars_on_P"]
    states: dict[int, list[int]] = {
        leaf_scalars[0] % CONTROL_SUBGROUP_ORDER: [0]
    }
    layer_records: list[dict[str, Any]] = [
        {
            "after_leaf_count": 1,
            "backpointer_path_count": 1,
            "state_scalars": sorted(states),
        }
    ]
    backpointer_edges: list[dict[str, Any]] = []

    for leaf_index in range(1, M - 1):
        wanted = internal_tokens[leaf_index - 1]
        next_states: dict[int, list[int]] = defaultdict(list)
        for parent_scalar in sorted(states):
            for parent_mask in sorted(states[parent_scalar]):
                for sign in (-1, 1):
                    child_scalar = (
                        parent_scalar + sign * leaf_scalars[leaf_index]
                    ) % CONTROL_SUBGROUP_ORDER
                    actual = scalar_kummer_token(
                        child_scalar,
                        base,
                        CONTROL_P,
                        CONTROL_SUBGROUP_ORDER,
                    )
                    if actual != wanted:
                        continue
                    child_mask = parent_mask
                    if sign == 1:
                        child_mask |= 1 << (leaf_index - 1)
                    next_states[child_scalar].append(child_mask)
                    backpointer_edges.append(
                        {
                            "child_scalar": child_scalar,
                            "leaf_index_zero_based": leaf_index,
                            "parent_mask": parent_mask,
                            "parent_scalar": parent_scalar,
                            "sign": sign,
                            "tail_mask": child_mask,
                        }
                    )
        states = {
            scalar: sorted(masks)
            for scalar, masks in sorted(next_states.items())
        }
        layer_records.append(
            {
                "after_leaf_count": leaf_index + 1,
                "backpointer_path_count": sum(
                    len(masks) for masks in states.values()
                ),
                "state_scalars": sorted(states),
            }
        )

    accepted: list[dict[str, int]] = []
    final_leaf_index = M - 1
    for parent_scalar in sorted(states):
        for parent_mask in sorted(states[parent_scalar]):
            for sign in (-1, 1):
                terminal_scalar = (
                    parent_scalar
                    + sign * leaf_scalars[final_leaf_index]
                ) % CONTROL_SUBGROUP_ORDER
                if terminal_scalar not in (
                    CONTROL_TARGET_SCALAR,
                    CONTROL_SUBGROUP_ORDER - CONTROL_TARGET_SCALAR,
                ):
                    continue
                terminal_mask = parent_mask
                if sign == 1:
                    terminal_mask |= 1 << (final_leaf_index - 1)
                orientation = (
                    1
                    if terminal_scalar == CONTROL_TARGET_SCALAR
                    else -1
                )
                accepted.append(
                    {
                        "sign_mask_tail_15": terminal_mask,
                        "target_orientation": orientation,
                        "terminal_scalar": terminal_scalar,
                    }
                )
                backpointer_edges.append(
                    {
                        "child_scalar": terminal_scalar,
                        "leaf_index_zero_based": final_leaf_index,
                        "parent_mask": parent_mask,
                        "parent_scalar": parent_scalar,
                        "sign": sign,
                        "tail_mask": terminal_mask,
                    }
                )
    accepted.sort(
        key=lambda item: (
            item["sign_mask_tail_15"],
            item["target_orientation"],
        )
    )
    return {
        "accepted": accepted,
        "backpointer_edges": backpointer_edges,
        "layers": layer_records,
    }


def build_control_recovery_replay() -> dict[str, Any]:
    if math.prod(FACTOR_CHAIN) != D or CONTROL_P - 1 != D:
        raise AssertionError("control degree/field contract failed")
    if not is_prime_trial(CONTROL_P):
        raise AssertionError("control modulus is not prime")
    if curve_discriminant(CONTROL_P, CONTROL_A, CONTROL_B) == 0:
        raise AssertionError("control curve is singular")
    actual_curve_order = curve_order(CONTROL_P, CONTROL_A, CONTROL_B)
    if actual_curve_order != CONTROL_CURVE_ORDER:
        raise AssertionError("control curve order changed")
    if (
        math.prod(CONTROL_CURVE_ORDER_FACTORS) != actual_curve_order
        or not all(
            is_prime_trial(value)
            for value in CONTROL_CURVE_ORDER_FACTORS
        )
    ):
        raise AssertionError("control curve-order factorization failed")

    rational_two_torsion_x = [
        x
        for x in range(CONTROL_P)
        if curve_rhs(x, CONTROL_P, CONTROL_A, CONTROL_B) == 0
    ]
    if rational_two_torsion_x:
        raise AssertionError("control curve gained rational two-torsion")
    if not on_curve(
        CONTROL_SEED, CONTROL_P, CONTROL_A, CONTROL_B
    ):
        raise AssertionError("control seed is off curve")

    base = scalar_mul(
        CONTROL_COFACTOR,
        CONTROL_SEED,
        CONTROL_P,
        CONTROL_A,
        CONTROL_B,
    )
    if base is None or scalar_mul(
        CONTROL_SUBGROUP_ORDER,
        base,
        CONTROL_P,
        CONTROL_A,
        CONTROL_B,
    ) is not None:
        raise AssertionError("control base-point order failed")
    repeated = scalar_mul(
        CONTROL_REPEATED_SCALAR,
        base,
        CONTROL_P,
        CONTROL_A,
        CONTROL_B,
    )
    target = scalar_mul(
        CONTROL_TARGET_SCALAR,
        base,
        CONTROL_P,
        CONTROL_A,
        CONTROL_B,
    )
    if repeated is None or target is None:
        raise AssertionError("control distinguished point is identity")
    for point in (base, repeated, target):
        if point is None or point[0] == 0 or pow(
            point[0], D, CONTROL_P
        ) != 1:
            raise AssertionError("control membership check failed")

    ordering_records, preimages = enumerate_control_preimages(base)
    order_by_index = {
        item["ordering_index"]: item for item in ordering_records
    }
    fibers: dict[
        tuple[int, tuple[str | int, ...]], list[dict[str, Any]]
    ] = defaultdict(list)
    for preimage in preimages:
        key = (
            preimage["ordering_index"],
            tuple(preimage["internal_tokens"]),
        )
        fibers[key].append(preimage)
    if len(fibers) != 239:
        raise AssertionError("projective fiber count mismatch")

    fiber_summaries: list[dict[str, Any]] = []
    all_backpointer_edges: list[dict[str, Any]] = []
    accepted_pairs: list[dict[str, int]] = []
    identity_fiber_full: dict[str, Any] | None = None
    exact_preimage_group_checks = 0
    for fiber_index, (key, source_preimages) in enumerate(
        sorted(
            fibers.items(),
            key=lambda item: (
                item[0][0],
                tuple(str(value) for value in item[0][1]),
            ),
        )
    ):
        ordering_index, token_tuple = key
        ordering = order_by_index[ordering_index]
        replay = replay_supplied_internal_fiber(
            ordering, list(token_tuple), base
        )
        expected = sorted(
            [
                {
                    "sign_mask_tail_15": item["sign_mask_tail_15"],
                    "target_orientation": item["target_orientation"],
                    "terminal_scalar": (
                        CONTROL_TARGET_SCALAR
                        if item["target_orientation"] == 1
                        else CONTROL_SUBGROUP_ORDER
                        - CONTROL_TARGET_SCALAR
                    ),
                }
                for item in source_preimages
            ],
            key=lambda item: (
                item["sign_mask_tail_15"],
                item["target_orientation"],
            ),
        )
        if replay["accepted"] != expected:
            raise AssertionError("supplied-coordinate DP mismatch")
        identity_sizes = sorted(
            {
                size
                for item in source_preimages
                for size in item["identity_prefix_sizes"]
            }
        )
        has_identity = bool(identity_sizes)

        for edge in replay["backpointer_edges"]:
            all_backpointer_edges.append(
                {"fiber_index": fiber_index, **edge}
            )
        for item in replay["accepted"]:
            accepted_pairs.append(
                {
                    "ordering_index": ordering_index,
                    "sign_mask_tail_15": item["sign_mask_tail_15"],
                    "target_orientation": item["target_orientation"],
                }
            )

        leaf_scalars = ordering["leaf_scalars_on_P"]
        for source in source_preimages:
            signs = [1] + [
                1
                if (source["sign_mask_tail_15"] >> (index - 1)) & 1
                else -1
                for index in range(1, M)
            ]
            raw_sum: Point = None
            normalized_sum: Point = None
            orientation = source["target_orientation"]
            for sign, scalar in zip(signs, leaf_scalars, strict=True):
                point = scalar_mul(
                    scalar, base, CONTROL_P, CONTROL_A, CONTROL_B
                )
                raw_sum = point_add(
                    raw_sum,
                    point if sign == 1 else point_neg(point, CONTROL_P),
                    CONTROL_P,
                    CONTROL_A,
                    CONTROL_B,
                )
                normalized_sign = orientation * sign
                normalized_sum = point_add(
                    normalized_sum,
                    point
                    if normalized_sign == 1
                    else point_neg(point, CONTROL_P),
                    CONTROL_P,
                    CONTROL_A,
                    CONTROL_B,
                )
            expected_raw = (
                target
                if orientation == 1
                else point_neg(target, CONTROL_P)
            )
            if raw_sum != expected_raw or normalized_sum != target:
                raise AssertionError("control exact point replay failed")
            exact_preimage_group_checks += 1

        summary = {
            "accepted_masks": [
                item["sign_mask_tail_15"] for item in replay["accepted"]
            ],
            "affine_admissible": not has_identity,
            "backpointer_edge_count": len(replay["backpointer_edges"]),
            "fiber_index": fiber_index,
            "identity_prefix_sizes": identity_sizes,
            "internal_coordinates_sha256": digest(
                [token_record(token) for token in token_tuple]
            ),
            "layer_backpointer_path_counts": [
                item["backpointer_path_count"]
                for item in replay["layers"]
            ],
            "layer_state_widths": [
                len(item["state_scalars"]) for item in replay["layers"]
            ],
            "ordering_index": ordering_index,
            "preimage_count": len(source_preimages),
            "target_orientations": [
                item["target_orientation"] for item in replay["accepted"]
            ],
        }
        fiber_summaries.append(summary)
        if has_identity:
            if identity_fiber_full is not None:
                raise AssertionError("multiple identity fibers found")
            identity_fiber_full = {
                **summary,
                "backpointer_edges": replay["backpointer_edges"],
                "internal_coordinates": [
                    token_record(token) for token in token_tuple
                ],
                "layers": replay["layers"],
                "repeated_positions_zero_based": ordering[
                    "repeated_positions_zero_based"
                ],
            }

    accepted_pairs.sort(
        key=lambda item: (
            item["ordering_index"],
            item["sign_mask_tail_15"],
            item["target_orientation"],
        )
    )
    if identity_fiber_full is None:
        raise AssertionError("identity fiber is missing")
    affine_fibers = sum(
        item["affine_admissible"] for item in fiber_summaries
    )
    identity_fibers = sum(
        bool(item["identity_prefix_sizes"]) for item in fiber_summaries
    )
    multiplicity_profile = dict(
        sorted(
            Counter(
                item["preimage_count"] for item in fiber_summaries
            ).items()
        )
    )
    if (
        len(accepted_pairs) != 240
        or affine_fibers != 238
        or identity_fibers != 1
        or identity_fiber_full["preimage_count"] != 2
        or identity_fiber_full["accepted_masks"] != [0, 32_766]
        or identity_fiber_full["identity_prefix_sizes"] != [2]
        or multiplicity_profile != {1: 238, 2: 1}
        or len(all_backpointer_edges) != 3_599
        or exact_preimage_group_checks != 240
    ):
        raise AssertionError("control fiber accounting failed")

    normalized_rows: set[tuple[int, int, int]] = set()
    for preimage in preimages:
        ordering = order_by_index[preimage["ordering_index"]]
        repeated_positions = set(
            ordering["repeated_positions_zero_based"]
        )
        signs = [1] + [
            1
            if (preimage["sign_mask_tail_15"] >> (index - 1)) & 1
            else -1
            for index in range(1, M)
        ]
        orientation = preimage["target_orientation"]
        base_coefficient = orientation * sum(
            signs[index]
            for index in range(M)
            if index not in repeated_positions
        )
        repeated_coefficient = orientation * sum(
            signs[index] for index in repeated_positions
        )
        normalized_rows.add(
            (
                base_coefficient % CONTROL_SUBGROUP_ORDER,
                repeated_coefficient % CONTROL_SUBGROUP_ORDER,
                CONTROL_SUBGROUP_ORDER - 1,
            )
        )
    if normalized_rows != {
        (
            CONTROL_TARGET_SCALAR,
            0,
            CONTROL_SUBGROUP_ORDER - 1,
        )
    }:
        raise AssertionError("control normalized row is not unique")
    compressed_check = point_add(
        scalar_mul(
            CONTROL_TARGET_SCALAR,
            base,
            CONTROL_P,
            CONTROL_A,
            CONTROL_B,
        ),
        point_neg(target, CONTROL_P),
        CONTROL_P,
        CONTROL_A,
        CONTROL_B,
    )
    if compressed_check is not None:
        raise AssertionError("control normalized row does not close")

    return {
        "field": {
            "p": CONTROL_P,
            "D": D,
            "factor_chain": list(FACTOR_CHAIN),
            "p_minus_one_equals_D": True,
            "curve": "y^2 = x^3 + 7",
            "curve_order": actual_curve_order,
            "curve_order_factors": list(CONTROL_CURVE_ORDER_FACTORS),
            "rational_two_torsion_x": rational_two_torsion_x,
        },
        "subgroup": {
            "order": CONTROL_SUBGROUP_ORDER,
            "cofactor": CONTROL_COFACTOR,
            "seed": point_record(CONTROL_SEED),
            "P": point_record(base),
            "repeated_50P": point_record(repeated),
            "target_R_14P": point_record(target),
            "order_check": "[3463]P = O",
        },
        "coordinate_multiset": [
            {
                "basis": "P",
                "multiplicity": 14,
                "scalar_on_P": CONTROL_BASE_SCALAR,
                "x": base[0],
            },
            {
                "basis": "50P",
                "multiplicity": 2,
                "scalar_on_P": CONTROL_REPEATED_SCALAR,
                "x": repeated[0],
            },
        ],
        "ordered_topologies": {
            "unique_orders": len(ordering_records),
            "definition": (
                "lexicographic choices of the two zero-based positions "
                "occupied by 50P"
            ),
            "records_sha256": digest(ordering_records),
            "first": ordering_records[0],
            "last": ordering_records[-1],
        },
        "supplied_internal_dp": {
            "first_leaf_sign_normalization": "+1",
            "leaf_state_rule": (
                "start at the positive lift of leaf 1; for each later leaf "
                "try both lifts"
            ),
            "supplied_coordinate_rule": (
                "after leaves 2 through 15 retain a point state exactly "
                "when its Kummer coordinate equals the supplied [U_i:V_i]"
            ),
            "identity_state_rule": "retain O as [1:0] in projective mode",
            "terminal_rule": "accept exactly R or -R after leaf 16",
            "all_projective_fibers_replayed": True,
            "backpointer_edge_count": len(all_backpointer_edges),
            "backpointer_edges_sha256": digest(all_backpointer_edges),
            "fiber_summaries_sha256": digest(fiber_summaries),
            "accepted_terminal_records_sha256": digest(accepted_pairs),
            "ordinary_layer_state_widths": [1] * 15,
            "ordinary_backpointer_edges_per_fiber": 15,
            "identity_fiber": identity_fiber_full,
        },
        "fiber_accounting": {
            "unique_orders": len(ordering_records),
            "normalized_preimages": len(preimages),
            "preimage_records_sha256": digest(preimages),
            "projective_fibers": len(fibers),
            "affine_fibers": affine_fibers,
            "identity_fibers": identity_fibers,
            "identity_fiber_masks": identity_fiber_full[
                "accepted_masks"
            ],
            "fiber_preimage_multiplicity_profile": {
                str(key): value
                for key, value in multiplicity_profile.items()
            },
        },
        "normalized_row": {
            "basis_coefficients_mod_3463": {
                "P": CONTROL_TARGET_SCALAR,
                "50P": 0,
            },
            "target": "R",
            "target_coefficient_mod_3463": (
                CONTROL_SUBGROUP_ORDER - 1
            ),
            "display": "14P - R = O",
            "preimage_count": len(preimages),
            "duplicate_aggregation": "the two 50P coefficients sum to zero",
        },
        "exact_group_checks": {
            "all_240_raw_leaf_sums_equal_oriented_target": True,
            "all_240_target_normalized_leaf_sums_equal_R": True,
            "normalized_row_sum": point_record(compressed_check),
        },
        "hashes": {
            "fiber_summaries": digest(fiber_summaries),
            "backpointer_edges": digest(all_backpointer_edges),
            "normalized_row": digest(
                {
                    "P": CONTROL_TARGET_SCALAR,
                    "50P": 0,
                    "R": CONTROL_SUBGROUP_ORDER - 1,
                }
            ),
        },
    }


def build_secp256k1_glv_replay() -> dict[str, Any]:
    if SECP_P % 4 != 3:
        raise AssertionError("fixed square-root shortcut is unavailable")
    y_candidate = pow(8, (SECP_P + 1) // 4, SECP_P)
    if y_candidate * y_candidate % SECP_P != 8:
        raise AssertionError("x=1 does not lift to secp256k1")
    p0_y = y_candidate if y_candidate % 2 == 0 else SECP_P - y_candidate
    p0: Point = (1, p0_y)
    if not on_curve(p0, SECP_P):
        raise AssertionError("P0 is off secp256k1")
    if (
        pow(SECP_BETA, 3, SECP_P) != 1
        or SECP_BETA == 1
        or (
            SECP_BETA * SECP_BETA + SECP_BETA + 1
        )
        % SECP_P
        != 0
    ):
        raise AssertionError("beta is not the expected cube root")
    if (
        pow(SECP_LAMBDA, 3, SECP_N) != 1
        or SECP_LAMBDA == 1
        or (
            SECP_LAMBDA * SECP_LAMBDA + SECP_LAMBDA + 1
        )
        % SECP_N
        != 0
    ):
        raise AssertionError("lambda is not the expected cube root")

    phi_p0: Point = (SECP_BETA, p0_y)
    phi2_p0: Point = (SECP_BETA * SECP_BETA % SECP_P, p0_y)
    positive_orbit = [p0, phi_p0, phi2_p0]
    if not all(on_curve(point, SECP_P) for point in positive_orbit):
        raise AssertionError("phi orbit left secp256k1")
    if len(set(positive_orbit)) != 3:
        raise AssertionError("positive phi orbit is not size three")
    if scalar_mul(SECP_N, p0, SECP_P) is not None:
        raise AssertionError("P0 did not pass the group-order check")
    if scalar_mul(SECP_LAMBDA, p0, SECP_P) != phi_p0:
        raise AssertionError("lambda action does not match phi(P0)")
    lambda_squared = SECP_LAMBDA * SECP_LAMBDA % SECP_N
    if scalar_mul(lambda_squared, p0, SECP_P) != phi2_p0:
        raise AssertionError("lambda^2 action does not match phi^2(P0)")
    orbit_sum: Point = None
    for point in positive_orbit:
        orbit_sum = point_add(orbit_sum, point, SECP_P)
    if orbit_sum is not None:
        raise AssertionError("P0 + phi(P0) + phi^2(P0) did not close")

    signed_orbit = [
        *positive_orbit,
        *[point_neg(point, SECP_P) for point in positive_orbit],
    ]
    if len(set(signed_orbit)) != 6:
        raise AssertionError("signed GLV orbit is not size six")

    leaf_rows: list[dict[str, Any]] = []
    raw_leaf_sum: Point = None
    for index in range(14):
        epsilon = 1 if index < 7 else -1
        leaf_rows.append(
            {
                "epsilon": epsilon,
                "index_one_based": index + 1,
                "point": "P0",
                "x": 1,
            }
        )
        raw_leaf_sum = point_add(
            raw_leaf_sum,
            p0 if epsilon == 1 else point_neg(p0, SECP_P),
            SECP_P,
        )
    for label, point in (("phi(P0)", phi_p0), ("phi^2(P0)", phi2_p0)):
        leaf_rows.append(
            {
                "epsilon": -1,
                "index_one_based": len(leaf_rows) + 1,
                "point": label,
                "x": point[0],
            }
        )
        raw_leaf_sum = point_add(
            raw_leaf_sum, point_neg(point, SECP_P), SECP_P
        )
    if len(leaf_rows) != M or raw_leaf_sum != p0:
        raise AssertionError("fixed M16 GLV leaf sum is not P0")
    raw_relation = point_add(
        raw_leaf_sum, point_neg(p0, SECP_P), SECP_P
    )
    if raw_relation is not None:
        raise AssertionError("fixed M16 GLV row does not close")
    membership_checks = [
        {
            "index_one_based": item["index_one_based"],
            "x": item["x"],
            "x_to_D_mod_p": pow(item["x"], D, SECP_P),
        }
        for item in leaf_rows
    ]
    if (
        D % 3 != 0
        or any(item["x_to_D_mod_p"] != 1 for item in membership_checks)
        or pow(1, D, SECP_P) != 1
    ):
        raise AssertionError("fixed M16 GLV membership replay failed")

    representative = point_neg(p0, SECP_P)
    if representative is None:
        raise AssertionError("representative unexpectedly is identity")
    signed_lift_rows = [
        {
            "base_point": "P0",
            "epsilon_counts": {"+1": 7, "-1": 7},
            "eta": -1,
            "j": 0,
            "relation_to_representative": "P0 = -phi^0(-P0)",
            "coefficient_contribution_mod_n": 0,
        },
        {
            "base_point": "phi(P0)",
            "epsilon": -1,
            "eta": -1,
            "j": 1,
            "relation_to_representative": "phi(P0) = -phi^1(-P0)",
            "coefficient_contribution_mod_n": SECP_LAMBDA,
        },
        {
            "base_point": "phi^2(P0)",
            "epsilon": -1,
            "eta": -1,
            "j": 2,
            "relation_to_representative": "phi^2(P0) = -phi^2(-P0)",
            "coefficient_contribution_mod_n": lambda_squared,
        },
    ]
    compressed_coefficient = (
        SECP_LAMBDA + lambda_squared
    ) % SECP_N
    if compressed_coefficient != SECP_N - 1:
        raise AssertionError("GLV compressed coefficient is not -1")
    compressed_leaf_point = scalar_mul(
        compressed_coefficient, representative, SECP_P
    )
    if compressed_leaf_point != p0:
        raise AssertionError("compressed leaf term is not P0")
    compressed_relation = point_add(
        compressed_leaf_point, point_neg(p0, SECP_P), SECP_P
    )
    if compressed_relation is not None:
        raise AssertionError("compressed GLV row does not close")

    return {
        "field_and_curve": {
            "p": SECP_P,
            "n": SECP_N,
            "curve": "y^2 = x^3 + 7",
            "D": D,
            "D_divisible_by_3": D % 3 == 0,
            "beta": SECP_BETA,
            "lambda": SECP_LAMBDA,
            "beta_polynomial_check_mod_p": (
                SECP_BETA * SECP_BETA + SECP_BETA + 1
            )
            % SECP_P,
            "lambda_polynomial_check_mod_n": (
                SECP_LAMBDA * SECP_LAMBDA + SECP_LAMBDA + 1
            )
            % SECP_N,
        },
        "P0": {
            **point_record(p0),
            "definition": "the even-y lift of x=1",
            "rhs": 8,
            "n_multiple": point_record(scalar_mul(SECP_N, p0, SECP_P)),
        },
        "phi_orbit": {
            "positive": [
                {
                    "j": index,
                    "point": point_record(point),
                    "x_rule": (
                        f"beta^{index} mod p"
                        if index
                        else "1"
                    ),
                    "y_is_even": point[1] % 2 == 0,
                }
                for index, point in enumerate(positive_orbit)
                if point is not None
            ],
            "negative": [
                {
                    "j": index,
                    "point": point_record(point_neg(point, SECP_P)),
                }
                for index, point in enumerate(positive_orbit)
            ],
            "positive_orbit_size": 3,
            "signed_orbit_size": 6,
            "orbit_sum": point_record(orbit_sum),
        },
        "m16_membership_row": {
            "leaf_count": len(leaf_rows),
            "leaves": leaf_rows,
            "membership_checks": membership_checks,
            "target": "P0",
            "target_coefficient": -1,
            "semantic_identity": (
                "seven P0 minus seven P0 minus phi(P0) minus "
                "phi^2(P0) minus P0 = O"
            ),
            "construction": "fixed theorem identity with no target search",
        },
        "representative": {
            "label": "-P0",
            "point": point_record(representative),
            "selection": "fixed deterministic signed-orbit representative",
        },
        "signed_lift_rows": signed_lift_rows,
        "coefficient_replay": {
            "rule": (
                "a signed occurrence epsilon*Q with "
                "Q=eta*phi^j(representative) contributes "
                "epsilon*eta*lambda^j modulo n"
            ),
            "lambda_squared_mod_n": lambda_squared,
            "eta_minus_one_rows": 3,
            "leaf_coefficient_on_representative_mod_n": (
                compressed_coefficient
            ),
            "leaf_coefficient_display": "-1",
            "target_coefficient": -1,
            "compressed_row": "-(-P0) - P0 = O",
        },
        "exact_group_checks": {
            "lambda_P0_equals_phi_P0": True,
            "lambda_squared_P0_equals_phi_squared_P0": True,
            "raw_leaf_sum": point_record(raw_leaf_sum),
            "raw_relation_sum": point_record(raw_relation),
            "compressed_leaf_term": point_record(compressed_leaf_point),
            "compressed_relation_sum": point_record(compressed_relation),
            "raw_and_compressed_close": True,
        },
        "theorem_bindings": {
            "whole_group_membership": (
                "Ecdlp.Curve.secp256k1_mem_zmultiples"
            ),
            "glv_eigenvalue": (
                "Ecdlp.Curve."
                "secp256k1_glvPoint_eq_lam_on_zmultiples"
            ),
            "glv_orbit": (
                "Ecdlp.Curve.secp256k1_glvPoint_orbit_three_distinct"
            ),
            "curve_cardinality": (
                "Ecdlp.Curve.secp256k1_card_point_eq_n"
            ),
            "no_nonzero_two_torsion": (
                "Ecdlp.Curve.secp256k1_no_nonzero_two_torsion"
            ),
        },
    }


def frozen_predicates() -> dict[str, Any]:
    internal_variables = [
        f"W_{index}=[U_{index}:V_{index}]"
        for index in range(2, M)
    ]
    equations = ["H(Q_1,Q_2,W_2)=0"]
    equations.extend(
        f"H(W_{index - 1},Q_{index},W_{index})=0"
        for index in range(3, M)
    )
    equations.append("H(W_15,Q_16,Q_T)=0")
    return {
        "algebraic_closure_projective_semantics": {
            "name": "GeoCat_kbar",
            "field_scope": (
                "nonsingular E:y^2=x^3+7 with char(k) not in {2,3,7}"
            ),
            "external_domain": "Q_1,...,Q_16,Q_T in P1(k)",
            "internal_domain": "W_2,...,W_15 in P1(algebraic_closure(k))",
            "equations": equations,
            "internal_variables": internal_variables,
            "status": "frozen",
        },
        "fp_rational_projective_internals": {
            "name": "RatCat_Fp",
            "field_scope": (
                "p not in {2,3,7}; discriminant(E) is nonzero"
            ),
            "external_domain": "Q_1,...,Q_16,Q_T in P1(F_p)",
            "internal_domain": "W_2,...,W_15 in P1(F_p)",
            "equations": equations,
            "status": "frozen",
        },
        "affine_chart": {
            "name": "AffCat_Fp",
            "parent": "RatCat_Fp",
            "field_scope": (
                "p not in {2,3,7}; discriminant(E) is nonzero"
            ),
            "localization": "V_2*...*V_15 != 0",
            "dehomogenization": "W_i=[u_i:1]",
            "identity_excluded": True,
            "status": "frozen",
        },
        "base_recovery": {
            "name": "Recover_Fp",
            "field_scope": (
                "p not in {2,3,7}; discriminant(E) is nonzero"
            ),
            "inputs": (
                "ordered leaf coordinates, supplied projective internals, "
                "and full target point R"
            ),
            "leaf_requirement": "every finite leaf has an E(F_p) lift",
            "method": "exact point-state DP with retained backpointers",
            "terminal_requirement": "the final state is R or -R",
            "status": "frozen",
        },
        "direct_S17": {
            "name": "DirectS17",
            "predicate_defined": False,
            "polynomial_frozen": False,
            "status": "unresolved_not_frozen",
            "reason": (
                "the repository has no frozen recursive projective "
                "definition and no reverse theorem above S4"
            ),
        },
    }


def leaf_lift_partition() -> dict[str, Any]:
    return {
        "exhaustive_nonoverlapping": True,
        "field_scope": (
            "nonsingular E:y^2=x^3+7 over F_p with p not in {2,3,7}"
        ),
        "normalization": (
            "a valid finite [X:Z] has x=X/Z; a valid Z=0 coordinate "
            "normalizes to O=[1:0]"
        ),
        "types": [
            {
                "id": "invalid_projective",
                "condition": "[X:Z]=[0:0]",
                "geometric_lifts": 0,
                "frobenius_type": "undefined",
                "base_recovery": "reject INVALID_PROJECTIVE",
            },
            {
                "id": "identity",
                "condition": "Z=0 and X!=0",
                "normalized_coordinate": "[1:0]",
                "geometric_lifts": 1,
                "lift": "O",
                "frobenius_type": "plus",
                "base_recovery": "retain the identity point",
            },
            {
                "id": "finite_base_pair",
                "condition": "Z!=0 and chi(x^3+7)=+1",
                "geometric_lifts": 2,
                "lifts": "P and -P in E(F_p)",
                "frobenius_type": "plus",
                "base_recovery": "retain both signed lifts",
            },
            {
                "id": "finite_extension_pair",
                "condition": "Z!=0 and chi(x^3+7)=-1",
                "geometric_lifts": 2,
                "lifts": "P and -P in E(F_(p^2))",
                "frobenius_equation": "pi(P)=-P",
                "frobenius_type": "minus",
                "base_recovery": "reject EXTERNAL_NONLIFT",
            },
            {
                "id": "finite_rational_two_torsion",
                "condition": "Z!=0 and x^3+7=0",
                "geometric_lifts": 1,
                "lift": "T=(x,0)=-T in E(F_p)[2]",
                "frobenius_type": "plus",
                "base_recovery": "retain one lift and collapse sign aliases",
            },
        ],
    }


def local_transition_partition() -> dict[str, Any]:
    return {
        "exhaustive_nonoverlapping_for_valid_inputs": True,
        "field_scope": (
            "nonsingular E:y^2=x^3+7 over F_p with p not in {2,3,7}"
        ),
        "priority": [
            "invalid_projective_input",
            "identity_input_duplicate",
            "repeated_two_torsion_duplicate",
            "repeated_tangent",
            "distinct_two_torsion_duplicate",
            "distinct_rational_split",
            "distinct_extension_only",
        ],
        "types": [
            {
                "id": "invalid_projective_input",
                "condition": "one input is [0:0]",
                "root_structure": "undefined",
                "disposition": "reject INVALID_PROJECTIVE",
            },
            {
                "id": "identity_input_duplicate",
                "condition": "at least one valid input is O",
                "formula": (
                    "H(O,[X:Z],[U:V])=(X*V-Z*U)^2"
                ),
                "root_structure": "the other coordinate, multiplicity 2",
                "disposition": "retain one point state, not two aliases",
            },
            {
                "id": "repeated_two_torsion_duplicate",
                "condition": "finite a=b and f(a)=a^3+7=0",
                "formula": "H([a:1],[a:1],[U:V])=c*V^2 with c!=0",
                "root_structure": "O, multiplicity 2",
                "disposition": "retain O and collapse the two local signs",
            },
            {
                "id": "repeated_tangent",
                "condition": "finite a=b and f(a)!=0",
                "formula": (
                    "H([a:1],[a:1],[U:V])="
                    "V*(-4*f(a)*U+(a^4-56*a)*V)"
                ),
                "root_structure": "O and kappa(2P), each multiplicity 1",
                "disposition": (
                    "keep both projective branches; affine mode keeps only "
                    "kappa(2P)"
                ),
            },
            {
                "id": "distinct_two_torsion_duplicate",
                "condition": "finite a!=b and f(a)*f(b)=0",
                "discriminant": "16*f(a)*f(b)=0",
                "root_structure": "one finite F_p coordinate, multiplicity 2",
                "disposition": "retain one state and collapse sign aliases",
            },
            {
                "id": "distinct_rational_split",
                "condition": (
                    "finite a!=b and chi(f(a)*f(b))=+1"
                ),
                "discriminant": "16*f(a)*f(b), a nonzero square",
                "root_structure": "two distinct roots in P1(F_p)",
                "disposition": "retain both exact point branches",
            },
            {
                "id": "distinct_extension_only",
                "condition": (
                    "finite a!=b and chi(f(a)*f(b))=-1"
                ),
                "discriminant": "16*f(a)*f(b), a nonsquare",
                "root_structure": (
                    "two conjugate simple roots in P1(F_(p^2)); "
                    "no root in P1(F_p)"
                ),
                "disposition": "reject INTERNAL_EXTENSION_ONLY in F_p mode",
            },
        ],
        "duplicate_root_sources": [
            "identity_input_duplicate",
            "repeated_two_torsion_duplicate",
            "distinct_two_torsion_duplicate",
        ],
        "duplicate_policy": (
            "algebraic multiplicity never creates another point state, "
            "backpointer, or relation row"
        ),
    }


def recovery_disposition_partition() -> dict[str, Any]:
    return {
        "partition_rule": "apply the first matching row in priority order",
        "exhaustive_nonoverlapping": True,
        "field_scope": (
            "nonsingular E:y^2=x^3+7 over F_p with p not in {2,3,7}"
        ),
        "rows": [
            {
                "priority": 1,
                "id": "INVALID_PROJECTIVE",
                "condition": "some coordinate pair is [0:0]",
                "geometric_projective": "excluded",
                "fp_projective": "excluded",
                "affine": "excluded",
                "base_recovery": "reject",
            },
            {
                "priority": 2,
                "id": "EXTERNAL_NONLIFT",
                "condition": (
                    "all coordinates are valid and some finite leaf has "
                    "chi(f(x))=-1"
                ),
                "geometric_projective": "allowed",
                "fp_projective": "may be allowed",
                "affine": "may be allowed",
                "base_recovery": "reject before row emission",
            },
            {
                "priority": 3,
                "id": "INTERNAL_EXTENSION_ONLY",
                "condition": (
                    "all finite leaves lift over F_p, but a required local "
                    "root is present only over an extension"
                ),
                "geometric_projective": "allowed",
                "fp_projective": "absent",
                "affine": "absent",
                "base_recovery": "reject",
            },
            {
                "priority": 4,
                "id": "IDENTITY_PREFIX",
                "condition": (
                    "base recovery succeeds and at least one supplied "
                    "internal coordinate has V_i=0"
                ),
                "geometric_projective": "accept",
                "fp_projective": "accept",
                "affine": "reject",
                "base_recovery": "accept with an explicit O state",
            },
            {
                "priority": 5,
                "id": "RATIONAL_TWO_TORSION",
                "condition": (
                    "no earlier row matches and some retained lift has y=0"
                ),
                "geometric_projective": "accept",
                "fp_projective": "accept",
                "affine": "accept if every internal V_i!=0",
                "base_recovery": "accept after sign-alias collapse",
            },
            {
                "priority": 6,
                "id": "REPEATED_TANGENT",
                "condition": (
                    "no earlier row matches and a repeated finite input "
                    "uses its tangent output"
                ),
                "geometric_projective": "accept",
                "fp_projective": "accept",
                "affine": "accept",
                "base_recovery": "accept with exact branch backpointer",
            },
            {
                "priority": 7,
                "id": "ORDINARY_RATIONAL",
                "condition": "none of the earlier rows matches",
                "geometric_projective": "accept",
                "fp_projective": "accept",
                "affine": "accept",
                "base_recovery": "accept after both exact curve checks",
            },
        ],
        "post_acceptance_normalizations": {
            "topology_permutations": (
                "keep the ordered leaf tuple, coordinate multiset, signed "
                "point multiset, and normalized row as distinct objects; "
                "replay each order because prefix admissibility depends on it"
            ),
            "glv_lift_signs": (
                "retain eta in Q=eta*phi^j(P0) and use "
                "epsilon*eta*lambda^j modulo n"
            ),
        },
    }


def build_artifact() -> dict[str, Any]:
    prior_path = REPO_ROOT / PRIOR_ARTIFACT
    if not prior_path.exists():
        raise FileNotFoundError(f"missing prior artifact: {prior_path}")
    actual_prior_sha = hashlib.sha256(prior_path.read_bytes()).hexdigest()
    if actual_prior_sha != PRIOR_SHA256:
        raise AssertionError(
            "prior semantic-bridge artifact digest does not match contract"
        )
    source_paths = (
        "tasks/ECDLP_RESEARCH.md",
        PRIMARY_CLAIM_EXTRACT,
        "Ecdlp/Proved/SemaevThree.lean",
        "Ecdlp/Proved/SemaevFour.lean",
        "Ecdlp/Proved/CurveCardinalityExact.lean",
        "Ecdlp/Proved/CurveFullGroup.lean",
        "Ecdlp/Proved/GlvSubgroupEigenvalue.lean",
        "Ecdlp/Proved/GlvOrbit.lean",
    )
    missing_source_paths = [
        path for path in source_paths if not (REPO_ROOT / path).is_file()
    ]
    if missing_source_paths:
        raise FileNotFoundError(
            f"missing source paths: {missing_source_paths}"
        )
    primary_claim_extract_path = REPO_ROOT / PRIMARY_CLAIM_EXTRACT
    actual_primary_claim_extract_sha = hashlib.sha256(
        primary_claim_extract_path.read_bytes()
    ).hexdigest()
    if actual_primary_claim_extract_sha != PRIMARY_CLAIM_EXTRACT_SHA256:
        raise AssertionError("primary claim extract digest changed")

    small_13 = exhaustive_small_field_replay(13)
    small_11 = exhaustive_small_field_replay(11)
    expected_13 = {
        "identity_input_duplicate": 27,
        "repeated_tangent": 13,
        "distinct_rational_split": 96,
        "distinct_extension_only": 60,
    }
    expected_11 = {
        "identity_input_duplicate": 23,
        "repeated_two_torsion_duplicate": 1,
        "repeated_tangent": 10,
        "distinct_two_torsion_duplicate": 20,
        "distinct_rational_split": 40,
        "distinct_extension_only": 50,
    }
    if small_13["transition_type_counts"] != dict(sorted(expected_13.items())):
        raise AssertionError("F_13 transition partition changed")
    if small_11["transition_type_counts"] != dict(sorted(expected_11.items())):
        raise AssertionError("F_11 transition partition changed")

    control = build_control_recovery_replay()
    glv = build_secp256k1_glv_replay()
    equations = frozen_predicates()
    return {
        "artifact_id": ARTIFACT_ID,
        "schema_version": SCHEMA_VERSION,
        "kind": (
            "deterministic_nonexperimental_set_theoretic_"
            "exceptional_fiber_certificate"
        ),
        "depends_on": {
            "artifact": PRIOR_ARTIFACT,
            "required_sha256": PRIOR_SHA256,
            "observed_sha256": actual_prior_sha,
            "digest_match": True,
        },
        "source_scope": {
            "task_contract_anchor": "tasks/ECDLP_RESEARCH.md#task-017",
            "task016_artifact": PRIOR_ARTIFACT,
            "task016_artifact_sha256": PRIOR_SHA256,
            "primary_claim_extract": PRIMARY_CLAIM_EXTRACT,
            "primary_claim_extract_sha256": (
                PRIMARY_CLAIM_EXTRACT_SHA256
            ),
            "primary_claim_extract_observed_sha256": (
                actual_primary_claim_extract_sha
            ),
            "primary_claim_extract_digest_match": True,
            "source_claim_ids": list(SOURCE_CLAIM_IDS),
            "semaev_three": "Ecdlp/Proved/SemaevThree.lean",
            "semaev_four": "Ecdlp/Proved/SemaevFour.lean",
            "curve_cardinality": (
                "Ecdlp/Proved/CurveCardinalityExact.lean"
            ),
            "curve_full_group": "Ecdlp/Proved/CurveFullGroup.lean",
            "glv_eigenvalue": (
                "Ecdlp/Proved/GlvSubgroupEigenvalue.lean"
            ),
            "glv_orbit": "Ecdlp/Proved/GlvOrbit.lean",
            "all_listed_paths_exist": True,
            "canonical_policy_or_generated_files_hashed": False,
        },
        "scope": {
            "included": [
                "homogeneous projective S3 left-fold semantics",
                "finite-field lift and local-root classification",
                "supplied-internal-coordinate point recovery",
                "ordered topology and duplicate accounting",
                "fixed secp256k1 GLV sign replay",
            ],
            "excluded": [
                "S17 expansion or evaluation",
                "any materialized polynomial system",
                "Sage, msolve, F4, Groebner, or solver execution",
                "exact-target relation search",
                "discrete-log computation",
                "rank, yield, or cost accounting",
                "experiment authorization",
                "hypothesis retention",
                "route promotion",
            ],
        },
        "claim_boundaries": {
            "result_scope": "set_theoretic",
            "global_s17_equivalence": "not_claimed",
            "scheme_equivalence": "not_claimed",
            "radicality": "not_claimed",
            "multiplicity_equality": "not_claimed",
            "coordinate_difference_saturation": "forbidden",
        },
        "frozen_predicates": equations,
        "projective_s3": {
            "name": "H=S3h",
            "curve": (
                "nonsingular E:y^2=x^3+7 over k with "
                "char(k) not in {2,3,7}"
            ),
            "field_scope": (
                "char(k) not in {2,3,7}, equivalently the discriminant "
                "-16*27*7^2 is nonzero in k"
            ),
            "kummer_coordinate": {
                "identity": "kappa(O)=[1:0]",
                "affine": "kappa((x,y))=[x:1]",
            },
            "homogeneous_polynomial": (
                "X1^2*X2^2*Z3^2 + X1^2*Z2^2*X3^2 + "
                "Z1^2*X2^2*X3^2 - 2*X1^2*X2*Z2*X3*Z3 - "
                "2*X1*Z1*X2^2*X3*Z3 - "
                "2*X1*Z1*X2*Z2*X3^2 - "
                "28*(X1*Z1*Z2^2*Z3^2 + "
                "Z1^2*X2*Z2*Z3^2 + Z1^2*Z2^2*X3*Z3)"
            ),
            "multidegree": [2, 2, 2],
            "affine_coefficients_z2_z_1": [
                "(x1-x2)^2",
                "-2*((x1+x2)*(x1*x2)+14)",
                "(x1*x2)^2-28*(x1+x2)",
            ],
            "exact_local_formulas": {
                "distinct_factorization": (
                    "H(kappa(P),kappa(Q),[U:V])="
                    "(x(P)-x(Q))^2*(U-x(P+Q)*V)*"
                    "(U-x(P-Q)*V)"
                ),
                "distinct_discriminant": (
                    "Disc_U/V H=16*f(x(P))*f(x(Q)), f(x)=x^3+7"
                ),
                "repeated": (
                    "H([x:1],[x:1],[U:V])="
                    "V*(-4*f(x)*U+(x^4-56*x)*V)"
                ),
                "identity": (
                    "H([1:0],[X:Z],[U:V])=(X*V-Z*U)^2"
                ),
            },
            "projective_validity": (
                "every coordinate pair must differ from [0:0]"
            ),
            "saturation_policy": (
                "remove only components supported on a projective "
                "coordinate pair [0:0]; never remove coordinate-equality "
                "loci"
            ),
            "irrelevant_ideal_saturation": {
                "coordinate_pair_ideals": [
                    *[
                        f"<X_{index},Z_{index}>"
                        for index in range(1, M + 1)
                    ],
                    "<X_T,Z_T>",
                    *[
                        f"<U_{index},V_{index}>"
                        for index in range(2, M)
                    ],
                ],
                "irrelevant_ideal_B": (
                    "product of all 31 listed coordinate-pair ideals"
                ),
                "saturated_ideal": "I_cat : B^infinity",
                "set_theoretic_effect": (
                    "exclude the union of loci on which any projective "
                    "coordinate pair is [0:0]"
                ),
                "forbidden_extra_saturands": [
                    "X_i*Z_j-X_j*Z_i",
                    "U_i*V_j-U_j*V_i",
                    "all coordinate differences",
                ],
            },
            "scheme_claim": "none; every bridge claim is set-theoretic",
        },
        "bridge_theorem": {
            "assumptions": [
                "E/k is the nonsingular curve y^2=x^3+7",
                "char(k) not in {2,3,7}",
                "the curve discriminant -16*27*7^2 is nonzero in k",
            ],
            "local_lemma": (
                "for P,Q over the algebraic closure of such a field, "
                "H(kappa(P),"
                "kappa(Q),W)=0 iff W=kappa(P+Q) or W=kappa(P-Q)"
            ),
            "local_case_split": [
                "distinct finite inputs",
                "repeated finite non-two-torsion inputs",
                "repeated finite two-torsion inputs",
                "at least one identity input",
            ],
            "global_projective_tree": (
                "induction over the 15 left-fold vertices gives "
                "GeoCat_kbar iff the chosen external Kummer coordinates "
                "admit a signed-point relation over the algebraic closure"
            ),
            "fp_projective_tree": (
                "when every external coordinate has an E(F_p) lift, "
                "RatCat_Fp iff a base-field signed relation exists"
            ),
            "affine_chart": (
                "AffCat_Fp iff such a relation exists with every fixed-order "
                "prefix of sizes 2 through 15 nonidentity"
            ),
            "proof_method": "exact local formulas followed by induction",
            "status": "exact_set_theoretic_bridge",
            "direct_S17_bridge": "unresolved_not_frozen",
        },
        "frobenius_classification": {
            "field_scope": (
                "E/F_p is nonsingular and p not in {2,3,7}"
            ),
            "plus_space": "E_plus=ker(pi-1)=E(F_p)",
            "minus_space": "E_minus=ker(pi+1)",
            "prefix_decomposition": "A=B+T with B in E_plus and T in E_minus",
            "rational_kummer_criterion": (
                "kappa(A) in P1(F_p) iff pi(A)=A or pi(A)=-A "
                "iff 2T=O or 2B=O"
            ),
            "secp256k1_specialization": (
                "absence of rational two-torsion reduces the criterion "
                "to T=O or B=O"
            ),
            "topology_consequence": (
                "an order is projectively F_p-admissible exactly when every "
                "prefix satisfies the criterion; affine admissibility also "
                "requires every prefix to differ from O"
            ),
        },
        "leaf_lift_types": leaf_lift_partition(),
        "local_transition_types": local_transition_partition(),
        "recovery_dispositions": recovery_disposition_partition(),
        "small_field_replays": {
            "F13_no_rational_two_torsion": small_13,
            "F11_with_rational_two_torsion": small_11,
        },
        "control_recovery_replay": control,
        "secp256k1_glv_replay": glv,
        "terminal_disposition": {
            "scientific_disposition": "scoped_blocker",
            "completed_scope": (
                "exact set-theoretic homogeneous projective-tree to "
                "signed-point bridge, including all named local strata and "
                "base-recovery normalization"
            ),
            "remaining_blocker": (
                "the direct S17 predicate is not frozen, and no reverse "
                "theorem above S4 is present"
            ),
            "next_mathematical_step": (
                "freeze a recursive projective definition of S17 with "
                "declared resultant degrees, then test a projective "
                "resultant induction against the frozen tree predicate"
            ),
            "cell_status": "open_non_executable",
            "experiment_permission": "none",
            "retention_disposition": "zero_retention_success",
            "cost_quantity_transition": "partial_to_partial",
            "barrier_transition": "open_to_open",
            "cell_transition": "open_to_open",
            "authorization": "none",
            "route_effect": "none",
            "hypothesis_effect": "none",
            "rank_status": "unpriced",
            "yield_status": "unpriced",
            "cost_quantity_status": "partial",
            "solving_cost_status": "unpriced",
            "barrier_effect": "narrowed_open",
            "assurance": "certificate_replayed",
            "source_independence": "not_established",
            "calibration": "excluded_nonexperimental",
        },
        "unresolved_fields": [
            "a frozen direct S17 definition",
            "a reverse direct-S17 theorem above S4",
            "radicality or scheme-level multiplicity comparison",
        ],
        "producer_checks": {
            "prior_digest_bound": True,
            "primary_claim_extract_digest_bound": True,
            "all_source_paths_exist": True,
            "nonsingular_curve_scope_enforced": True,
            "excluded_characteristics": list(EXCLUDED_CHARACTERISTICS),
            "small_fields_exhaustive": [11, 13],
            "control_projective_fibers_replayed": 239,
            "control_normalized_preimages_replayed": 240,
            "control_backpointer_edges_replayed": 3_599,
            "secp_m16_leaf_count": 16,
            "secp_raw_group_check": True,
            "secp_compressed_group_check": True,
            "direct_S17_materialized": False,
        },
    }


def write_artifact(artifact: dict[str, Any]) -> str:
    payload = canonical_bytes(artifact)
    artifact_sha = hashlib.sha256(payload).hexdigest()
    ARTIFACT_PATH.write_bytes(payload)
    HASH_PATH.write_text(
        f"{artifact_sha}  artifact.json\n", encoding="utf-8"
    )
    return artifact_sha


def check_artifact(artifact: dict[str, Any]) -> str:
    expected_payload = canonical_bytes(artifact)
    if not ARTIFACT_PATH.exists() or not HASH_PATH.exists():
        raise FileNotFoundError("artifact.json or artifact.sha256 is missing")
    actual_payload = ARTIFACT_PATH.read_bytes()
    if actual_payload != expected_payload:
        raise AssertionError("artifact.json is not at the producer fixpoint")
    actual_sha = hashlib.sha256(actual_payload).hexdigest()
    expected_hash_line = f"{actual_sha}  artifact.json\n"
    if HASH_PATH.read_text(encoding="utf-8") != expected_hash_line:
        raise AssertionError("artifact.sha256 is stale")
    return actual_sha


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify that committed outputs equal a fresh deterministic build",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    artifact = build_artifact()
    artifact_sha = (
        check_artifact(artifact) if args.check else write_artifact(artifact)
    )
    action = "checked" if args.check else "wrote"
    print(f"{action} {ARTIFACT_PATH}")
    print(f"sha256 {artifact_sha}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, FileNotFoundError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
