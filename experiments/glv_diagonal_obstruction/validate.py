#!/usr/bin/env python3
"""Independently replay the GLV diagonal-action obstruction certificate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ARTIFACT_PATH = HERE / "artifact.json"
DIGEST_PATH = HERE / "artifact.sha256"

# Frozen independently of the producer artifact. Changing the witness requires
# review of both entrypoints rather than trusting producer-supplied parameters.
P = 1009
A = 0
B = 11
BETA = 374


def fail(message: str) -> None:
    raise ValueError(message)


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2
    return True


def roots_for_x(x: int) -> int:
    rhs = (x * x * x + A * x + B) % P
    return sum(1 for y in range(P) if y * y % P == rhs)


def expected_artifact() -> dict[str, object]:
    if not is_prime(P):
        fail("frozen modulus is not prime")
    if BETA == 1 or pow(BETA, 3, P) != 1:
        fail("beta is not a nontrivial cube root of unity")
    if (BETA * BETA + BETA + 1) % P != 0:
        fail("beta does not satisfy beta^2 + beta + 1 = 0")

    on_curve_x = [x for x in range(P) if roots_for_x(x) > 0]
    if 0 in on_curve_x:
        fail("the witness requires the C3 action to be free on x-coordinates")

    fibers: dict[int, list[int]] = {}
    for x in on_curve_x:
        fibers.setdefault(x * x * x % P, []).append(x)
    for u, fiber in fibers.items():
        if len(fiber) != 3:
            fail(f"cube fiber {u} has size {len(fiber)}, expected 3")
        orbit = {fiber[0], BETA * fiber[0] % P, BETA * BETA * fiber[0] % P}
        if set(fiber) != orbit:
            fail(f"cube fiber {u} is not one diagonal C3 orbit")

    diagonal_pairs = [[x, BETA * x % P] for x in on_curve_x]
    same_cube_pairs = sorted(
        [x1, x2]
        for fiber in fibers.values()
        for x1 in fiber
        for x2 in fiber
    )
    diagonal_set = {tuple(pair) for pair in diagonal_pairs}
    overidentified = [
        pair for pair in same_cube_pairs if tuple(pair) not in diagonal_set
    ]
    point_count = 1 + sum(roots_for_x(x) for x in range(P))

    return {
        "schema_version": 1,
        "certificate_id": "GLV-DIAGONAL-OBSTRUCTION-P1009-M2",
        "claim_boundary": (
            "Exact finite witness that coordinatewise cubes forget relative "
            "C3 phase. This is not a Semaev attack run or a complexity no-go."
        ),
        "parameters": {
            "field_p": P,
            "curve_a": A,
            "curve_b": B,
            "beta": BETA,
            "arity_m": 2,
        },
        "raw": {
            "on_curve_x": on_curve_x,
            "cube_fibers": [
                {"u": u, "x": sorted(fiber)}
                for u, fiber in sorted(fibers.items())
            ],
            "diagonal_action_graph_pairs": diagonal_pairs,
            "coordinatewise_same_cube_pairs": same_cube_pairs,
            "overidentified_pairs": overidentified,
        },
        "measurements": {
            "curve_point_count": point_count,
            "on_curve_x_count": len(on_curve_x),
            "cube_image_count": len(fibers),
            "diagonal_action_graph_count": len(diagonal_pairs),
            "coordinatewise_same_cube_count": len(same_cube_pairs),
            "overidentified_pair_count": len(overidentified),
            "coordinatewise_to_diagonal_ratio": 3,
            "overidentified_fraction": "2/3",
        },
        "diagonal_invariant_presentation_m2": {
            "generators": {
                "a": [3, 0],
                "b": [2, 1],
                "c": [1, 2],
                "d": [0, 3],
            },
            "toric_relations": [
                "b^2-a*c",
                "b*c-a*d",
                "c^2-b*d",
            ],
        },
    }


def validate_toric_relations(artifact: dict[str, object]) -> None:
    presentation = artifact["diagonal_invariant_presentation_m2"]
    generators = presentation["generators"]
    if generators != {
        "a": [3, 0],
        "b": [2, 1],
        "c": [1, 2],
        "d": [0, 3],
    }:
        fail("unexpected invariant generators")

    def add(left: list[int], right: list[int]) -> tuple[int, int]:
        return left[0] + right[0], left[1] + right[1]

    if add(generators["b"], generators["b"]) != add(
        generators["a"], generators["c"]
    ):
        fail("b^2 = a*c exponent identity failed")
    if add(generators["b"], generators["c"]) != add(
        generators["a"], generators["d"]
    ):
        fail("b*c = a*d exponent identity failed")
    if add(generators["c"], generators["c"]) != add(
        generators["b"], generators["d"]
    ):
        fail("c^2 = b*d exponent identity failed")

    degree_three = [
        [i, 3 - i] for i in range(4)
    ]
    if sorted(generators.values()) != sorted(degree_three):
        fail("m=2 generators are not all four degree-three monomials")


def main() -> int:
    payload = ARTIFACT_PATH.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    expected_digest_record = f"{digest}  artifact.json\n"
    if DIGEST_PATH.read_text(encoding="ascii") != expected_digest_record:
        fail("artifact.sha256 does not match artifact.json")

    artifact = json.loads(payload)
    independently_recomputed = expected_artifact()
    if artifact != independently_recomputed:
        fail("artifact differs from independent exhaustive recomputation")
    validate_toric_relations(artifact)

    measurements = artifact["measurements"]
    expected_counts = {
        "curve_point_count": 967,
        "on_curve_x_count": 483,
        "cube_image_count": 161,
        "diagonal_action_graph_count": 483,
        "coordinatewise_same_cube_count": 1449,
        "overidentified_pair_count": 966,
        "coordinatewise_to_diagonal_ratio": 3,
        "overidentified_fraction": "2/3",
    }
    if measurements != expected_counts:
        fail(f"unexpected measurements: {measurements}")

    print(
        "VALIDATION: PASS "
        "(483 diagonal graph pairs, 1449 coordinatewise cube pairs, "
        "966 overidentified)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
