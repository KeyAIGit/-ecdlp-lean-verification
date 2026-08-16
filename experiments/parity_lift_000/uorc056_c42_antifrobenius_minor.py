#!/usr/bin/env python3
"""Exact C42 anti-Frobenius 2x2-minor decoder screen."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Iterator

from uorc056_c39_half_miller import TOYS, half_sequence

HELD_OUT = ((61, 61, (2, 25), 13, 47),)


def quadratic_character(value: int, prime: int) -> int:
    value %= prime
    if value == 0:
        return 0
    return 1 if pow(value, (prime - 1) // 2, prime) == 1 else -1


def projective_triples(prime: int) -> Iterator[tuple[int, int, int]]:
    """All points of P^2(F_p), normalized at the first nonzero coordinate."""
    for second in range(prime):
        for third in range(prime):
            yield 1, second, third
    for third in range(prime):
        yield 0, 1, third
    yield 0, 0, 1


def analyze_curve(
    row: tuple[int, int, tuple[int, int], int, int], label: str
) -> dict[str, Any]:
    curve, order, generator, shift, beta, lam, half, values = half_sequence(row)
    prime = curve.p
    samples: list[tuple[int, int, int]] = []
    for k in range(1, order):
        forward = values[k]
        reverse = values[order - k]
        cross = forward * reverse.conj()
        determinant_coefficient = (2 * cross.b) % prime
        symmetric_coefficient = (2 * cross.a) % prime
        if (forward * reverse.conj() - reverse * forward.conj()).a != 0:
            raise AssertionError("anti-Frobenius determinant is not pure imaginary")
        if (forward * reverse.conj() + reverse * forward.conj()).b != 0:
            raise AssertionError("Frobenius symmetric term is not in the base field")
        target = 1 if k % 2 == 0 else -1
        samples.append((determinant_coefficient, symmetric_coefficient, target))

    canonical_bits = {
        "determinant_lsb": all(
            (1 if determinant & 1 == 0 else -1) == target
            for determinant, symmetric, target in samples
        ),
        "determinant_lower_half": all(
            (1 if determinant < (prime + 1) // 2 else -1) == target
            for determinant, symmetric, target in samples
        ),
        "symmetric_lsb": all(
            (1 if symmetric & 1 == 0 else -1) == target
            for determinant, symmetric, target in samples
        ),
        "symmetric_lower_half": all(
            (1 if symmetric < (prime + 1) // 2 else -1) == target
            for determinant, symmetric, target in samples
        ),
    }

    candidates = 0
    survivors: list[dict[str, Any]] = []
    for first, second, constant in projective_triples(prime):
        candidates += 1
        normalized_phases: list[int] = []
        valid = True
        for determinant, symmetric, target in samples:
            value = (
                first * determinant + second * symmetric + constant
            ) % prime
            character = quadratic_character(value, prime)
            if character == 0:
                valid = False
                break
            normalized_phases.append(character * target)
        if valid and len(set(normalized_phases)) == 1:
            survivors.append({
                "coefficients": [first, second, constant],
                "phase": normalized_phases[0],
            })

    seen: dict[tuple[int, int], int] = {}
    mixed_collisions = 0
    for determinant, symmetric, target in samples:
        key = (determinant, symmetric)
        if key in seen and seen[key] != target:
            mixed_collisions += 1
        else:
            seen[key] = target

    return {
        "label": label,
        "p": prime,
        "n": order,
        "samples": order - 1,
        "projective_affine_character_candidates": candidates,
        "survivors": survivors,
        "survivor_count": len(survivors),
        "canonical_bits": canonical_bits,
        "distinct_minor_pairs": len(seen),
        "mixed_parity_collisions": mixed_collisions,
        "errors": 0,
    }


def build_minor_payload() -> dict[str, Any]:
    rows = [
        analyze_curve(row, f"frozen-{index + 1}")
        for index, row in enumerate(TOYS)
    ] + [
        analyze_curve(row, f"heldout-{index + 1}")
        for index, row in enumerate(HELD_OUT)
    ]
    payload: dict[str, Any] = {
        "profile_id": "UORC-056-C42-ANTIFROBENIUS-MINOR",
        "schema_version": "1.0",
        "grammar": (
            "chi_p(a*det_b(F(Q),F(-Q))+b*sym_a(F(Q),F(-Q))+c), "
            "(a:b:c) in P^2(F_p)"
        ),
        "curves": rows,
        "aggregate": {
            "curves": len(rows),
            "candidates": sum(
                int(row["projective_affine_character_candidates"])
                for row in rows
            ),
            "survivors": sum(int(row["survivor_count"]) for row in rows),
            "all_canonical_bits_fail": all(
                not any(bool(value) for value in row["canonical_bits"].values())
                for row in rows
            ),
            "errors": sum(int(row["errors"]) for row in rows),
        },
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["digest"] = hashlib.sha256(raw).hexdigest()
    return payload
