#!/usr/bin/env python3
"""Toy-only screen of public coordinate-adaptive division indices.

The rigidity theorem covers fixed integral-index pullbacks.  Here the index
m(Q) is selected from public canonical coordinate representatives and is then
used in an addition-chain evaluation of psi_m(Q).  This is an algorithmic,
piecewise category rather than a fixed algebraic section.

The frozen screen tests deterministic formulas shared across every toy curve,
measures exact carry/R3 decoding, matched-null significance, and additive
Fourier heaviness.  No external curve, point, key, wallet, or production-sized
target is accepted.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import random
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
MAX_PRODUCT_WEIGHT = 2


def canonical_index(value: int, order: int) -> int:
    return 1 + (value % (order - 1))


def scaled_index(value: int, source_modulus: int, order: int) -> int:
    value %= source_modulus
    return 1 + ((order - 1) * value // source_modulus)


def half_sign(value: int, modulus: int) -> int:
    value %= modulus
    if value == 0:
        return 0
    return 1 if 2 * value < modulus else -1


def field_carry(x: int, beta: int, p: int) -> int:
    x1 = beta * x % p
    x2 = beta * x1 % p
    total = x + x1 + x2
    if total == p:
        return 1
    if total == 2 * p:
        return 2
    raise AssertionError("field carry failed")


def index_formulas(x: int, y: int, p: int, order: int, beta: int, trace: int, lam: int) -> dict[str, int]:
    x0 = x % p
    x1 = beta * x0 % p
    x2 = beta * x1 % p
    xs = sorted((x0, x1, x2))
    gaps = (xs[1] - xs[0], xs[2] - xs[1], p + xs[0] - xs[2])
    u = pow(x0, 3, p)
    xy = x0 * y % p
    delta = field_carry(x0, beta, p)

    raw = {
        "x_mod_n": canonical_index(x0, order),
        "y_mod_n": canonical_index(y, order),
        "u_mod_n": canonical_index(u, order),
        "xy_mod_n": canonical_index(xy, order),
        "scaled_x": scaled_index(x0, p, order),
        "scaled_y": scaled_index(y, p, order),
        "scaled_u": scaled_index(u, p, order),
        "scaled_min_glv_x": scaled_index(xs[0], p, order),
        "scaled_mid_glv_x": scaled_index(xs[1], p, order),
        "scaled_max_glv_x": scaled_index(xs[2], p, order),
        "scaled_gap_0": scaled_index(gaps[0], p, order),
        "scaled_gap_1": scaled_index(gaps[1], p, order),
        "scaled_gap_2": scaled_index(gaps[2], p, order),
        "trace_times_x": canonical_index(trace * x0, order),
        "trace_times_y": canonical_index(trace * y, order),
        "lambda_or_square_by_half_y": lam if half_sign(y, p) == 1 else lam * lam % order,
        "trace_branch_by_field_carry": canonical_index(trace + (delta - 1) * (trace + 1), order),
        "glv_gap_rank_mix": canonical_index(xs[0] + 2 * xs[1] + 3 * xs[2], order),
    }
    return {name: max(1, min(order - 1, index)) for name, index in raw.items()}


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
    for weight in range(1, MAX_PRODUCT_WEIGHT + 1):
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
        positive = {k, lam*k % order, lam2*k % order}
        negative = {order-member for member in positive}
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
    index_formula_count: int
    candidate_vector_count: int
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

    psi_g = division_polynomial_evaluator(generator, p)
    rho = [0] + [quadratic_character(psi_g(k), p) for k in range(1, order)]
    chi_minus_one = quadratic_character(-1, p)
    point_scale = rho[order-1] * rho[1] * chi_minus_one
    if any(
        rho[order-k] != chi_minus_one * point_scale * rho[k]
        for k in range(1, order)
    ):
        raise AssertionError("residue negation scale failed")
    rho_kummer = all(rho[order-k] == rho[k] for k in range(1, order))

    sample_point = points[1]
    assert sample_point is not None
    formula_names = tuple(index_formulas(
        sample_point[0], sample_point[1], p, order, beta, trace, lam
    ).keys())

    signs: dict[str, list[int]] = {}
    for name in formula_names:
        signs[f"psi[m={name}]"] = []
        signs[f"C(mQ)*C(Q):{name}"] = []
        signs[f"half_y(mQ):{name}"] = []
        signs[f"chi_y(mQ):{name}"] = []

    public_c = [0] * order
    for k in range(1, order):
        public_c[k] = (point_scale if k & 1 else 1) * rho[k]

    for k in range(1, order):
        point = points[k]
        assert point is not None
        x, y = point
        formulas = index_formulas(x, y, p, order, beta, trace, lam)
        evaluator = division_polynomial_evaluator(point, p)
        for name, index in formulas.items():
            psi_value = quadratic_character(evaluator(index), p)
            if psi_value == 0:
                # index is nonzero modulo the prime subgroup order, so a zero
                # indicates an implementation or declared-order failure.
                raise AssertionError("adaptive division section vanished")
            signs[f"psi[m={name}]"].append(psi_value)

            target_scalar = index * k % order
            target_point = points[target_scalar]
            assert target_point is not None
            signs[f"C(mQ)*C(Q):{name}"].append(public_c[target_scalar] * public_c[k])
            signs[f"half_y(mQ):{name}"].append(half_sign(target_point[1], p))
            signs[f"chi_y(mQ):{name}"].append(quadratic_character(target_point[1], p))

    # GLV orbit norms of every adaptive observable.
    augmented = dict(signs)
    for name, values in list(signs.items()):
        augmented[f"N3({name})"] = [
            values[k-1]
            * values[(lam*k % order)-1]
            * values[(lam2*k % order)-1]
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
    rng = random.Random(20260812 + 71*p + order)
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
        index_formula_count=len(formula_names),
        candidate_vector_count=len(vectors),
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
        default=Path(__file__).with_name("adaptive_index_section_results.json"),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    large = [case for case in cases if case.order >= 500]
    payload = {
        "scope": (
            "fifteen frozen j=0 prime-order toy subgroups; "
            "no external point, key, wallet, or production target"
        ),
        "package": "ADAPTIVE-INDEX-SECTIONS-016",
        "category_escape": (
            "the division index m(Q) is selected from public coordinate "
            "representatives and is not a fixed algebraic pullback"
        ),
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases": len(cases),
            "index_formulas": max(case.index_formula_count for case in cases),
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
            "matched-null exceedance, or inverse-log-heavy spectrum for the same formula."
        ),
        "claim_boundary": [
            "Coordinate-to-index conversion is model-dependent but completely public.",
            "The candidate list was fixed before examining the frozen output.",
            "Toy significance does not prove a secp256k1 coefficient or complexity bound.",
            "No external or production-sized input is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
