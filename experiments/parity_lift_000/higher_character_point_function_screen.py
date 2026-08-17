#!/usr/bin/env python3
"""Toy-only screen of cubic and sextic phases of the public point function.

For a point P of odd order n over F_p, the raw point function is

    phi(P) = (W_P(p-1) / W_P(p-1+n))^(1/n^2).

On the frozen cases gcd(n^2,p-1)=1, so the root is unique in F_p.  The
committed point-function identity gives

    phi([k]G) = phi(G)^(k^2) W_G(k).

This package tests whether cubic or sextic characters of phi(Q), their C3
orbit products, and simple public y-orientations separate the GLV carry from
R3.  These characters stay in F_p and therefore do not incur the explicit
order-n cyclotomic embedding-degree barrier.

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
        raise AssertionError("n^2 root was not unique in F_p")
    exponent = pow((order * order) % (p - 1), -1, p - 1)
    return pow(numerator * pow(denominator, -1, p) % p, exponent, p)


def cubic_exponent(value: int, beta: int, p: int) -> int:
    phase = pow(value % p, (p - 1) // 3, p)
    if phase == 1:
        return 0
    if phase == beta:
        return 1
    if phase == beta * beta % p:
        return 2
    raise AssertionError("cubic character left mu_3")


def phase_signs(prefix: str, value: int, beta: int, p: int) -> dict[str, int]:
    exponent = cubic_exponent(value, beta, p)
    cubic_value = pow(value % p, (p - 1) // 3, p)
    sextic_value = pow(value % p, (p - 1) // 6, p)
    return {
        f"{prefix}:cubic_zero": 1 if exponent == 0 else -1,
        f"{prefix}:cubic_beta": 1 if exponent == 1 else -1,
        f"{prefix}:cubic_beta2": 1 if exponent == 2 else -1,
        f"{prefix}:cubic_integer_half": half_sign(cubic_value, p),
        f"{prefix}:sextic_integer_half": half_sign(sextic_value, p),
        f"{prefix}:quadratic": quadratic_character(value, p),
    }


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
    beta: int
    lam: int
    phi_generator: int
    point_scale_character: int
    rho_kummer_invariant: bool
    point_function_identity_checks: int
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
    point_scale = rho[order - 1] * rho[1] * chi_minus_one
    if quadratic_character(phi_g, p) != point_scale:
        raise AssertionError("point-scale character did not match raw point function")
    rho_kummer = all(rho[order-k] == rho[k] for k in range(1, order))

    phi_values = [0] * order
    direct_checks = 0
    for k in range(1, order):
        phi_values[k] = pow(phi_g, k * k, p) * psi_g(k) % p
        # Directly replay a sparse deterministic subset of public point-function
        # evaluations to bind the faster identity-generated sequence.
        if k <= 3 or k in {order//3, order//2, order-2, order-1}:
            point = points[k]
            assert point is not None
            if raw_point_function(point, order, p) != phi_values[k]:
                raise AssertionError("raw point-function identity failed")
            direct_checks += 1

    signs: dict[str, list[int]] = {}
    for k in range(1, order):
        point = points[k]
        assert point is not None
        x, y = point
        k1 = lam * k % order
        k2 = lam2 * k % order
        orbit_product = phi_values[k] * phi_values[k1] % p * phi_values[k2] % p
        ratio_01 = phi_values[k1] * pow(phi_values[k], -1, p) % p
        ratio_12 = phi_values[k2] * pow(phi_values[k1], -1, p) % p

        row: dict[str, int] = {}
        row.update(phase_signs("phi", phi_values[k], beta, p))
        row.update(phase_signs("orbit_product", orbit_product, beta, p))
        row.update(phase_signs("ratio_01", ratio_01, beta, p))
        row.update(phase_signs("ratio_12", ratio_12, beta, p))
        row["half_y"] = half_sign(y, p)
        row["chi_y"] = quadratic_character(y, p)
        row["half_x"] = half_sign(x, p)
        row["chi_x"] = quadratic_character(x, p)

        if not signs:
            signs = {name: [] for name in row}
        for name, sign in row.items():
            signs[name].append(sign)

    # Products with the two natural anti-Kummer orientations are generated by
    # the product pool below; include C3 norms of individual local phases too.
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
    rng = random.Random(20260812 + 83*p + order)
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
        point_function_identity_checks=direct_checks,
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
            "higher_character_point_function_results.json"
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
        "package": "HIGHER-CHARACTER-POINT-FUNCTION-017",
        "public_observable": (
            "raw point function phi(Q) in F_p, with cubic and sextic characters"
        ),
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases": len(cases),
            "point_function_identity_checks": sum(
                case.point_function_identity_checks for case in cases
            ),
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
            "matched-null exceedance, or inverse-log-heavy spectrum for the same phase formula."
        ),
        "claim_boundary": [
            "The raw point function is public through its defining ratio; the identity is used for fast frozen replay.",
            "Cubic and sextic phase signs are model-dependent deterministic maps from mu_3 and mu_6 to plus/minus one.",
            "Toy significance does not prove a secp256k1 identity or coefficient.",
            "No external or production-sized input is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
