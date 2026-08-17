#!/usr/bin/env python3
"""Toy-only screen of trace-scale and short-CM-index division sections.

Fixed small indices have bounded conductor.  This package instead tests public
indices of size about sqrt(n), arising from the Hasse trace and from a reduced
basis of

    L = {(u,v) in Z^2 : u + v*lambda = 0 mod n}.

Each division-polynomial value is still addition-chain evaluable in O(log n)
field operations.  The screen measures exact carry/R3 decoding and additive
Fourier heaviness across the frozen j=0 family.

No external curve, point, key, wallet, or production-sized target is accepted.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from nonlocal_odd_anchor_screen import (
    FROZEN_CASES,
    division_polynomial_evaluator,
    orbit,
    primitive_cube_root,
    quadratic_character,
)

NULL_TRIALS = 200
MAX_PRODUCT_WEIGHT = 3


def dot(a: tuple[int, int], b: tuple[int, int]) -> int:
    return a[0] * b[0] + a[1] * b[1]


def sub(a: tuple[int, int], q: int, b: tuple[int, int]) -> tuple[int, int]:
    return a[0] - q * b[0], a[1] - q * b[1]


def gauss_reduce(b1: tuple[int, int], b2: tuple[int, int]) -> tuple[tuple[int, int], tuple[int, int]]:
    while True:
        if dot(b2, b2) < dot(b1, b1):
            b1, b2 = b2, b1
        q = round(dot(b1, b2) / dot(b1, b1))
        reduced = sub(b2, q, b1)
        if dot(reduced, reduced) >= dot(b1, b1):
            return b1, reduced
        b2 = reduced


def cm_relation_vectors(order: int, lam: int) -> list[tuple[int, int]]:
    b1, b2 = gauss_reduce((order, 0), (-lam, 1))
    candidates = {
        b1,
        b2,
        (b1[0] + b2[0], b1[1] + b2[1]),
        (b1[0] - b2[0], b1[1] - b2[1]),
        (-b1[0], -b1[1]),
        (-b2[0], -b2[1]),
    }
    valid = [
        vector for vector in candidates
        if vector != (0, 0) and (vector[0] + vector[1] * lam) % order == 0
    ]
    return sorted(valid, key=lambda v: (dot(v, v), abs(v[0]) + abs(v[1]), v))[:4]


def bits(signs: list[int]) -> int:
    out = 0
    for i, sign in enumerate(signs):
        if sign == -1:
            out |= 1 << i
        elif sign != 1:
            raise AssertionError("non-binary sign")
    return out


def product_vectors(base: dict[str, int]) -> dict[int, str]:
    items = list(base.items())
    out: dict[int, str] = {}
    for weight in range(1, min(MAX_PRODUCT_WEIGHT, len(items)) + 1):
        for combination in itertools.combinations(items, weight):
            vector = 0
            names = []
            for name, value in combination:
                vector ^= value
                names.append(name)
            out.setdefault(vector, "*".join(names))
    return out


def best_accuracy(vectors: dict[int, str], target: int, length: int) -> tuple[float, str]:
    best = (0.5, "")
    for vector, name in vectors.items():
        distance = (vector ^ target).bit_count()
        accuracy = max(distance, length - distance) / length
        if accuracy > best[0] or (accuracy == best[0] and name < best[1]):
            best = accuracy, name
    return best


def spectrum(signs: list[int]) -> tuple[float, int, float, float]:
    vector = np.asarray([0] + signs, dtype=np.float64)
    transform = np.fft.fft(vector) / len(vector)
    magnitudes = np.abs(transform)
    magnitudes[0] = 0.0
    frequency = int(np.argmax(magnitudes))
    maximum = float(magnitudes[frequency])
    return maximum, frequency, maximum * math.sqrt(len(vector)), maximum * math.log(len(vector))


def carry_sign(k: int, lam: int, order: int) -> int:
    k1 = lam * k % order
    k2 = lam * k1 % order
    total = k + k1 + k2
    if total == order:
        return -1
    if total == 2 * order:
        return 1
    raise AssertionError("carry identity failed")


def random_anti_c6(order: int, lam: int, rng: random.Random) -> int:
    values = [0] * order
    visited: set[int] = set()
    lam2 = lam * lam % order
    for k in range(1, order):
        if k in visited:
            continue
        positive = {k, lam * k % order, lam2 * k % order}
        negative = {order - member for member in positive}
        sign = -1 if rng.getrandbits(1) else 1
        for member in positive:
            values[member] = sign
        for member in negative:
            values[member] = -sign
        visited.update(positive | negative)
    return bits(values[1:])


def random_kummer_c6(order: int, lam: int, rng: random.Random) -> int:
    values = [0] * order
    visited: set[int] = set()
    lam2 = lam * lam % order
    for k in range(1, order):
        if k in visited:
            continue
        orbit6 = {
            k, order-k,
            lam*k % order, order-(lam*k % order),
            lam2*k % order, order-(lam2*k % order),
        }
        sign = -1 if rng.getrandbits(1) else 1
        for member in orbit6:
            values[member] = sign
        visited.update(orbit6)
    return bits(values[1:])


@dataclass(frozen=True)
class CandidateMetric:
    name: str
    max_nonzero_fourier: float
    max_frequency: int
    coefficient_times_sqrt_order: float
    coefficient_times_log_order: float


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    generator: tuple[int, int]
    trace: int
    beta: int
    lam: int
    point_scale_character: int
    rho_kummer_invariant: bool
    cm_relation_vectors: tuple[tuple[int, int], ...]
    tested_indices: tuple[int, ...]
    candidate_vectors: int
    exact_carry_decoder: str | None
    exact_r3_decoder: str | None
    best_carry_accuracy: float
    best_carry_candidate: str
    carry_null_q95: float
    carry_empirical_percentile: float
    best_r3_accuracy: float
    best_r3_candidate: str
    r3_null_q95: float
    r3_empirical_percentile: float
    best_spectral_candidate: str
    best_spectral_coefficient: float
    best_spectral_times_sqrt_order: float
    best_spectral_times_log_order: float
    spectral_metrics: tuple[CandidateMetric, ...]


def run_case(p: int, order: int, generator: tuple[int, int]) -> CaseResult:
    points = orbit(generator, order, p)
    beta = primitive_cube_root(p)
    point_to_scalar = {point: scalar for scalar, point in enumerate(points)}
    lam = point_to_scalar[(beta * generator[0] % p, generator[1])]
    lam2 = lam * lam % order
    trace = p + 1 - order

    relations = cm_relation_vectors(order, lam)
    raw_indices = {
        abs(trace),
        abs(trace - 1),
        abs(trace + 1),
        min(p % order, (-p) % order),
        lam,
        lam2,
    }
    for u, v in relations:
        raw_indices.update({abs(u), abs(v), abs(u + v), abs(u - v)})
    indices = sorted(index for index in raw_indices if 2 <= index < order)

    psi_g = division_polynomial_evaluator(generator, p)
    rho = [0] + [quadratic_character(psi_g(k), p) for k in range(1, order)]
    chi_minus_one = quadratic_character(-1, p)
    point_scale = rho[order - 1] * rho[1] * chi_minus_one
    if any(
        rho[order-k] != chi_minus_one * point_scale * rho[k]
        for k in range(1, order)
    ):
        raise AssertionError("residue negation scale failed")
    rho_kummer = all(rho[order-k] == rho[k] for k in range(1, order))

    signs: dict[str, list[int]] = {f"psi_{index}": [] for index in indices}
    for relation_number, (u, v) in enumerate(relations):
        if abs(u) >= 2 and abs(v) >= 2:
            signs[f"CM_{relation_number}_unary_product"] = []

    for k in range(1, order):
        point = points[k]
        assert point is not None
        evaluator = division_polynomial_evaluator(point, p)
        values: dict[int, int] = {}
        for index in indices:
            value = quadratic_character(evaluator(index), p)
            if value == 0:
                raise AssertionError("trace-scale division section vanished")
            values[index] = value
            signs[f"psi_{index}"].append(value)

        phi_point = points[lam * k % order]
        assert phi_point is not None
        phi_evaluator = division_polynomial_evaluator(phi_point, p)
        for relation_number, (u, v) in enumerate(relations):
            if abs(u) < 2 or abs(v) < 2:
                continue
            left = quadratic_character(evaluator(abs(u)), p)
            right = quadratic_character(phi_evaluator(abs(v)), p)
            if u < 0:
                left *= chi_minus_one
            if v < 0:
                right *= chi_minus_one
            signs[f"CM_{relation_number}_unary_product"].append(left * right)

    augmented = dict(signs)
    for name, values in list(signs.items()):
        augmented[f"N3({name})"] = [
            values[k - 1]
            * values[(lam*k % order) - 1]
            * values[(lam2*k % order) - 1]
            for k in range(1, order)
        ]

    base_vectors = {name: bits(values) for name, values in augmented.items()}
    vectors = product_vectors(base_vectors)
    length = order - 1
    complement = (1 << length) - 1

    carry_target = bits([carry_sign(k, lam, order) for k in range(1, order)])
    r3_target = bits([
        rho[k] * rho[lam*k % order] * rho[lam2*k % order]
        for k in range(1, order)
    ])

    def exact(target: int) -> str | None:
        if target in vectors:
            return vectors[target]
        if target ^ complement in vectors:
            return "-" + vectors[target ^ complement]
        return None

    carry_observed = best_accuracy(vectors, carry_target, length)
    r3_observed = best_accuracy(vectors, r3_target, length)

    rng = random.Random(20260812 + 59*p + order)
    carry_null = sorted(
        best_accuracy(vectors, random_anti_c6(order, lam, rng), length)[0]
        for _ in range(NULL_TRIALS)
    )
    carry_q95 = carry_null[math.ceil(0.95*NULL_TRIALS)-1]

    if rho_kummer:
        r3_null = sorted(
            best_accuracy(vectors, random_kummer_c6(order, lam, rng), length)[0]
            for _ in range(NULL_TRIALS)
        )
        r3_q95 = r3_null[math.ceil(0.95*NULL_TRIALS)-1]
        r3_percentile = sum(value <= r3_observed[0] for value in r3_null)/NULL_TRIALS
    else:
        r3_q95 = 0.0
        r3_percentile = 0.0

    spectral_metrics: list[CandidateMetric] = []
    for name, values in sorted(augmented.items()):
        maximum, frequency, scaled_sqrt, scaled_log = spectrum(values)
        spectral_metrics.append(CandidateMetric(
            name=name,
            max_nonzero_fourier=maximum,
            max_frequency=frequency,
            coefficient_times_sqrt_order=scaled_sqrt,
            coefficient_times_log_order=scaled_log,
        ))
    spectral_best = max(
        spectral_metrics,
        key=lambda metric: (metric.max_nonzero_fourier, metric.name),
    )

    return CaseResult(
        p=p,
        order=order,
        generator=generator,
        trace=trace,
        beta=beta,
        lam=lam,
        point_scale_character=point_scale,
        rho_kummer_invariant=rho_kummer,
        cm_relation_vectors=tuple(relations),
        tested_indices=tuple(indices),
        candidate_vectors=len(vectors),
        exact_carry_decoder=exact(carry_target),
        exact_r3_decoder=exact(r3_target),
        best_carry_accuracy=carry_observed[0],
        best_carry_candidate=carry_observed[1],
        carry_null_q95=carry_q95,
        carry_empirical_percentile=(
            sum(value <= carry_observed[0] for value in carry_null)/NULL_TRIALS
        ),
        best_r3_accuracy=r3_observed[0],
        best_r3_candidate=r3_observed[1],
        r3_null_q95=r3_q95,
        r3_empirical_percentile=r3_percentile,
        best_spectral_candidate=spectral_best.name,
        best_spectral_coefficient=spectral_best.max_nonzero_fourier,
        best_spectral_times_sqrt_order=spectral_best.coefficient_times_sqrt_order,
        best_spectral_times_log_order=spectral_best.coefficient_times_log_order,
        spectral_metrics=tuple(spectral_metrics),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("trace_cm_index_section_results.json"),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    large = [case for case in cases if case.order >= 500]
    payload = {
        "scope": (
            "fifteen frozen j=0 prime-order toy subgroups; "
            "no external point, key, wallet, or production target"
        ),
        "package": "TRACE-CM-INDEX-SECTIONS-015",
        "index_sources": [
            "Hasse trace t and t+/-1",
            "p modulo subgroup order",
            "GLV lambda and lambda^2",
            "short vectors u+v*lambda=0 modulo n",
        ],
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases": len(cases),
            "exact_carry_decoders": sum(case.exact_carry_decoder is not None for case in cases),
            "exact_r3_decoders": sum(case.exact_r3_decoder is not None for case in cases),
            "large_carry_cases_strictly_above_null_q95": sum(
                case.best_carry_accuracy > case.carry_null_q95 for case in large
            ),
            "large_r3_cases_strictly_above_null_q95": sum(
                case.rho_kummer_invariant and case.best_r3_accuracy > case.r3_null_q95
                for case in large
            ),
            "large_cases_with_best_spectral_coefficient_ge_0_10": sum(
                case.best_spectral_coefficient >= 0.10 for case in large
            ),
            "large_cases_with_best_spectral_coefficient_ge_inverse_log": sum(
                case.best_spectral_coefficient >= 1/math.log(case.order) for case in large
            ),
            "largest_order": max(case.order for case in cases),
        },
        "decision_rule": (
            "A positive route requires a repeated cross-order exact decoder, "
            "matched-null exceedance, or inverse-log-heavy spectrum for the same construction."
        ),
        "claim_boundary": [
            "Products of unary division sections are a proxy for the corresponding short-CM net section.",
            "Toy Fourier heaviness does not itself prove a secp256k1 coefficient.",
            "Failure of this finite index family is not a lower bound for all order-dependent circuits.",
            "No external or production-sized input is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
