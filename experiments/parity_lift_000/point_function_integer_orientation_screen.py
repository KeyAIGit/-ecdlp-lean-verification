#!/usr/bin/env python3
"""Toy-only screen of integer orientations of the raw public point function.

The raw point function Phi(Q) is publicly evaluable in F_p and obeys

    Phi(-Q) = -Phi(Q),
    Phi(phi Q) = beta * Phi(Q)

on the j=0 family, up to the frozen normalization convention.  Unlike a
multiplicative character, the canonical integer representative can retain a
global branch cut.  The screen tests half-interval orientation, GLV field
carry, permutation orientation, orbit-product orientation, and bounded
products of these public predicates.

No external curve, point, key, wallet, or production-sized target is accepted.
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

NULL_TRIALS = 300
MAX_PRODUCT_WEIGHT = 3


def half_sign(value: int, modulus: int) -> int:
    value %= modulus
    if value == 0:
        return 0
    return 1 if 2 * value < modulus else -1


def raw_point_function(point: tuple[int, int], order: int, p: int) -> int:
    evaluator = division_polynomial_evaluator(point, p)
    numerator = evaluator(p - 1)
    denominator = evaluator(p - 1 + order)
    if numerator == 0 or denominator == 0:
        raise AssertionError("point-function defining ratio vanished")
    if math.gcd(order * order, p - 1) != 1:
        raise AssertionError("n^2 root was not unique")
    exponent = pow((order * order) % (p - 1), -1, p - 1)
    return pow(numerator * pow(denominator, -1, p) % p, exponent, p)


def field_carry_sign(value: int, beta: int, p: int) -> int:
    a0 = value % p
    a1 = beta * a0 % p
    a2 = beta * a1 % p
    total = a0 + a1 + a2
    if total == p:
        return -1
    if total == 2 * p:
        return 1
    raise AssertionError("point-function GLV coordinate carry failed")


def permutation_orientation(value: int, beta: int, p: int) -> int:
    a0 = value % p
    a1 = beta * a0 % p
    a2 = beta * a1 % p
    product = (a0 - a1) * (a1 - a2) * (a2 - a0)
    if product == 0:
        raise AssertionError("point-function GLV phase collided")
    return 1 if product > 0 else -1


def bits(signs: list[int]) -> int:
    out = 0
    for index, sign in enumerate(signs):
        if sign == -1:
            out |= 1 << index
        elif sign != 1:
            raise AssertionError("candidate was not binary")
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
    raise AssertionError("scalar carry identity failed")


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
    beta: int
    lam: int
    phi_generator: int
    point_scale_character: int
    rho_kummer_invariant: bool
    glv_scaling_checks: int
    negation_checks: int
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

    phi_g = raw_point_function(generator, order, p)
    psi_g = division_polynomial_evaluator(generator, p)
    rho = [0] + [quadratic_character(psi_g(k), p) for k in range(1, order)]
    chi_minus_one = quadratic_character(-1, p)
    point_scale = rho[order-1] * rho[1] * chi_minus_one
    rho_kummer = all(rho[order-k] == rho[k] for k in range(1, order))

    phi_values = [0] * order
    for k in range(1, order):
        phi_values[k] = pow(phi_g, k*k, p) * psi_g(k) % p

    # Determine the fixed GLV scaling root from the generator and verify it on
    # the entire frozen orbit rather than assuming a particular beta choice.
    glv_scale = phi_values[lam] * pow(phi_values[1], -1, p) % p
    if pow(glv_scale, 3, p) != 1:
        raise AssertionError("point-function GLV scale was not a cube root")

    signs: dict[str, list[int]] = {
        "half_phi": [],
        "chi_phi": [],
        "field_carry_phi": [],
        "permutation_phi": [],
        "half_phi_cube": [],
        "chi_phi_cube": [],
        "half_y": [],
        "chi_y": [],
        "field_carry_phi*half_y": [],
        "field_carry_phi*chi_y": [],
        "permutation_phi*half_y": [],
        "permutation_phi*chi_y": [],
        "half_phi*half_y": [],
        "half_phi*chi_y": [],
    }

    glv_checks = 0
    negation_checks = 0
    for k in range(1, order):
        k1 = lam*k % order
        k2 = lam2*k % order
        if phi_values[k1] != glv_scale * phi_values[k] % p:
            raise AssertionError("point-function GLV scaling failed")
        if phi_values[order-k] != (-phi_values[k]) % p:
            raise AssertionError("point-function negation failed")
        glv_checks += 1
        negation_checks += 1

        point = points[k]
        assert point is not None
        y = point[1]
        hphi = half_sign(phi_values[k], p)
        cphi = quadratic_character(phi_values[k], p)
        fc = field_carry_sign(phi_values[k], glv_scale, p)
        po = permutation_orientation(phi_values[k], glv_scale, p)
        cube = pow(phi_values[k], 3, p)
        hcube = half_sign(cube, p)
        ccube = quadratic_character(cube, p)
        hy = half_sign(y, p)
        cy = quadratic_character(y, p)

        row = {
            "half_phi": hphi,
            "chi_phi": cphi,
            "field_carry_phi": fc,
            "permutation_phi": po,
            "half_phi_cube": hcube,
            "chi_phi_cube": ccube,
            "half_y": hy,
            "chi_y": cy,
            "field_carry_phi*half_y": fc*hy,
            "field_carry_phi*chi_y": fc*cy,
            "permutation_phi*half_y": po*hy,
            "permutation_phi*chi_y": po*cy,
            "half_phi*half_y": hphi*hy,
            "half_phi*chi_y": hphi*cy,
        }
        for name, value in row.items():
            signs[name].append(value)

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
    length = order-1
    complement = (1 << length)-1
    carry_target = bits([carry_sign(k, lam, order) for k in range(1, order)])
    r3_target = bits([
        rho[k]*rho[lam*k % order]*rho[lam2*k % order]
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
    rng = random.Random(20260812 + 97*p + order)
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
        beta=beta,
        lam=lam,
        phi_generator=phi_g,
        point_scale_character=point_scale,
        rho_kummer_invariant=rho_kummer,
        glv_scaling_checks=glv_checks,
        negation_checks=negation_checks,
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
        default=Path(__file__).with_name(
            "point_function_integer_orientation_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    large = [case for case in cases if case.order >= 500]
    payload = {
        "scope": (
            "fifteen frozen j=0 prime-order toy subgroups; "
            "no external point, key, wallet, or production target"
        ),
        "package": "POINT-FUNCTION-INTEGER-ORIENTATION-019",
        "public_observable": "canonical integer representative of raw point function Phi(Q)",
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases": len(cases),
            "glv_scaling_checks": sum(case.glv_scaling_checks for case in cases),
            "negation_checks": sum(case.negation_checks for case in cases),
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
            "matched-null exceedance, or inverse-log-heavy spectrum for the same orientation formula."
        ),
        "claim_boundary": [
            "Canonical integer representatives are public but model-dependent and nonalgebraic.",
            "The point-function sequence is generated by its exact identity and directly checked on a deterministic subset.",
            "Toy significance does not prove a secp256k1 identity or Fourier coefficient.",
            "No external or production-sized input is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
