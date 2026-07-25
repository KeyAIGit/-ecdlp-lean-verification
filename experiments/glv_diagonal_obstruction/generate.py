#!/usr/bin/env python3
"""Generate the frozen GLV diagonal-action obstruction artifact."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ARTIFACT_PATH = HERE / "artifact.json"
DIGEST_PATH = HERE / "artifact.sha256"

P = 1009
A = 0
B = 11
BETA = 374


def y_count(rhs: int) -> int:
    rhs %= P
    if rhs == 0:
        return 1
    return 2 if pow(rhs, (P - 1) // 2, P) == 1 else 0


def build_artifact() -> dict[str, object]:
    on_curve_x = [
        x for x in range(P) if y_count(x * x * x + A * x + B) > 0
    ]
    cube_fibers: dict[int, list[int]] = {}
    for x in on_curve_x:
        cube_fibers.setdefault(pow(x, 3, P), []).append(x)

    diagonal_pairs = [[x, BETA * x % P] for x in on_curve_x]
    same_cube_pairs = sorted(
        [x1, x2]
        for fiber in cube_fibers.values()
        for x1 in fiber
        for x2 in fiber
    )
    diagonal_pair_set = {tuple(pair) for pair in diagonal_pairs}
    overidentified_pairs = [
        pair for pair in same_cube_pairs if tuple(pair) not in diagonal_pair_set
    ]
    point_count = 1 + sum(
        y_count(x * x * x + A * x + B) for x in range(P)
    )

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
                for u, fiber in sorted(cube_fibers.items())
            ],
            "diagonal_action_graph_pairs": diagonal_pairs,
            "coordinatewise_same_cube_pairs": same_cube_pairs,
            "overidentified_pairs": overidentified_pairs,
        },
        "measurements": {
            "curve_point_count": point_count,
            "on_curve_x_count": len(on_curve_x),
            "cube_image_count": len(cube_fibers),
            "diagonal_action_graph_count": len(diagonal_pairs),
            "coordinatewise_same_cube_count": len(same_cube_pairs),
            "overidentified_pair_count": len(overidentified_pairs),
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


def render(artifact: dict[str, object]) -> bytes:
    return (
        json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if the committed artifact or digest differs.",
    )
    args = parser.parse_args()

    payload = render(build_artifact())
    digest = hashlib.sha256(payload).hexdigest()
    digest_record = f"{digest}  artifact.json\n".encode("ascii")

    if args.check:
        problems = []
        if not ARTIFACT_PATH.is_file() or ARTIFACT_PATH.read_bytes() != payload:
            problems.append("artifact.json is stale")
        if not DIGEST_PATH.is_file() or DIGEST_PATH.read_bytes() != digest_record:
            problems.append("artifact.sha256 is stale")
        if problems:
            for problem in problems:
                print(f"ERROR: {problem}")
            return 1
        print(f"GENERATOR CHECK: PASS ({digest})")
        return 0

    ARTIFACT_PATH.write_bytes(payload)
    DIGEST_PATH.write_bytes(digest_record)
    print(f"wrote {ARTIFACT_PATH.relative_to(HERE.parent.parent)}")
    print(f"sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
