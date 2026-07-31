#!/usr/bin/env python3
"""Fault-injection checks for the independent torus desk validator."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
ARTIFACT = json.loads((HERE / "artifact.json").read_text(encoding="ascii"))


def write_case(directory: Path, document: dict[str, Any]) -> tuple[Path, Path]:
    raw = (
        json.dumps(document, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("ascii")
    artifact_path = directory / "artifact.json"
    hash_path = directory / "artifact.sha256"
    artifact_path.write_bytes(raw)
    hash_path.write_text(
        f"{hashlib.sha256(raw).hexdigest()}  artifact.json\n",
        encoding="ascii",
    )
    return artifact_path, hash_path


def must_reject(name: str, mutate: Callable[[dict[str, Any]], None]) -> None:
    document = deepcopy(ARTIFACT)
    mutate(document)
    with tempfile.TemporaryDirectory() as temporary:
        artifact_path, hash_path = write_case(Path(temporary), document)
        result = subprocess.run(
            [
                sys.executable,
                str(HERE / "validate.py"),
                "--artifact",
                str(artifact_path),
                "--hash-file",
                str(hash_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    if result.returncode == 0:
        raise AssertionError(f"validator accepted mutation {name}")


def main() -> int:
    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        (
            "hide-large-prime-step",
            lambda value: value["smooth_composition_screen"].__setitem__(
                "submitted_m6_m7_maximum_prime_degree_step", 2
            ),
        ),
        (
            "restore-false-arity-window",
            lambda value: value["audit_findings"].__setitem__(
                "exact_surviving_arities_under_size_and_conservative_linear_algebra_only",
                [6, 7],
            ),
        ),
        (
            "inflate-trace-root-count",
            lambda value: value["arity_rows"][4]["selected"].__setitem__(
                "trace_root_count", "45422601869677"
            ),
        ),
        (
            "promote-submitted-candidate",
            lambda value: value["assessment"].__setitem__(
                "submitted_candidate", "supported"
            ),
        ),
        (
            "erase-known-prior-art",
            lambda value: value["prior_art"].__setitem__(
                "classification", "not_found"
            ),
        ),
        (
            "inflate-two-power-divisor",
            lambda value: value["p_plus_one_factorization"].__setitem__(
                "largest_power_of_two_divisor", 32
            ),
        ),
        (
            "inflate-two-power-trace-count",
            lambda value: value["p_plus_one_factorization"].__setitem__(
                "largest_power_of_two_trace_root_count", 16
            ),
        ),
        (
            "authorize-experiment",
            lambda value: value["assessment"].__setitem__(
                "experiment_authorized", True
            ),
        ),
    ]
    for name, mutation in mutations:
        must_reject(name, mutation)
    print(
        "nonsplit-torus validator mutation tests PASS: "
        f"{len(mutations)}/{len(mutations)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
