#!/usr/bin/env python3
"""Toy-only screen of low jets of the compact pi-1 kernel section.

The isogeny pi-1 is evaluable as Frobenius minus identity even though its
separable degree is #E(F_p).  Its horizontal kernel polynomial P(Y) has one root
for every nonzero C3 orbit.  This script studies the first eight ordinary
Y-jets at those roots, their quadratic-character ratios, and C3 orbit norms.

A positive fixed-jet identity would be an order-dependent section outside the
fixed-degree C_quad screen.  No external point, key, wallet, or production-sized
target is accepted.
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

from nonlocal_odd_anchor_screen import (
    FROZEN_CASES,
    division_polynomial_evaluator,
    orbit,
    primitive_cube_root,
    quadratic_character,
)

JMAX = 8
MAX_PRODUCT_WEIGHT = 4
NULL_TRIALS = 200


def poly_mul(left: list[int], right: list[int], p: int) -> list[int]:
    out = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] = (out[i + j] + a * b) % p
    return out


def poly_from_roots(roots: list[int], p: int) -> list[int]:
    out = [1]
    for root in roots:
        out = poly_mul(out, [(-root) % p, 1], p)
    return out


def derivative(coefficients: list[int], p: int) -> list[int]:
    return [(i * coefficients[i]) % p for i in range(1, len(coefficients))]


def poly_eval(coefficients: list[int], value: int, p: int) -> int:
    out = 0
    for coefficient in reversed(coefficients):
        out = (out * value + coefficient) % p
    return out


def bits(signs: list[int]) -> int:
    out = 0
    for index, sign in enumerate(signs):
        if sign == -1:
            out |= 1 << index
        elif sign != 1:
            raise AssertionError("candidate was not binary")
    return out


def best_accuracy(vectors: dict[int, str], target: int, length: int) -> tuple[float, str, int]:
    best = (0.5, "", length // 2)
    for vector, name in vectors.items():
        distance = (vector ^ target).bit_count()
        matches = max(distance, length - distance)
        accuracy = matches / length
        if accuracy > best[0] or (accuracy == best[0] and name < best[1]):
            best = (accuracy, name, matches)
    return best


def products(base: dict[str, int]) -> dict[int, str]:
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
            k,
            order - k,
            lam * k % order,
            order - (lam * k % order),
            lam2 * k % order,
            order - (lam2 * k % order),
        }
        sign = -1 if rng.getrandbits(1) else 1
        for member in orbit6:
            values[member] = sign
        visited.update(orbit6)
    return bits(values[1:])


def scalar_carry_sign(k: int, lam: int, order: int) -> int:
    k1 = lam * k % order
    k2 = lam * k1 % order
    total = k + k1 + k2
    if total == order:
        return -1
    if total == 2 * order:
        return 1
    raise AssertionError("carry identity failed")


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    generator: tuple[int, int]
    beta: int
    lam: int
    point_scale_character: int
    rho_kummer_invariant: bool
    kernel_polynomial_degree: int
    nonvanishing_raw_jets: tuple[int, ...]
    raw_candidate_vectors: int
    orbit_candidate_vectors: int
    exact_carry_decoder: str | None
    exact_r3_decoder: str | None
    exact_normalized_orbit_decoder: str | None
    best_carry_accuracy: float
    best_carry_candidate: str
    carry_null_median: float
    carry_null_q95: float
    carry_empirical_percentile: float
    best_r3_accuracy: float
    best_r3_candidate: str
    r3_null_median: float
    r3_null_q95: float
    r3_empirical_percentile: float


def run_case(p: int, order: int, generator: tuple[int, int]) -> CaseResult:
    points = orbit(generator, order, p)
    beta = primitive_cube_root(p)
    point_to_scalar = {point: scalar for scalar, point in enumerate(points)}
    lam = point_to_scalar[(beta * generator[0] % p, generator[1])]
    lam2 = lam * lam % order

    roots: list[int] = []
    visited: set[int] = set()
    for k in range(1, order):
        if k in visited:
            continue
        c3 = {k, lam * k % order, lam2 * k % order}
        if len(c3) != 3:
            raise AssertionError("C3 orbit had wrong size")
        point = points[k]
        assert point is not None
        y = point[1]
        if any(points[member][1] != y for member in c3):
            raise AssertionError("C3 orbit did not share y")
        roots.append(y)
        visited.update(c3)

    polynomial = poly_from_roots(roots, p)
    jet_polynomials: dict[int, list[int]] = {}
    current = polynomial
    for jet in range(1, JMAX + 1):
        current = derivative(current, p)
        jet_polynomials[jet] = current

    psi = division_polynomial_evaluator(generator, p)
    rho = [0] + [quadratic_character(psi(k), p) for k in range(1, order)]
    chi_minus_one = quadratic_character(-1, p)
    point_scale = rho[order - 1] * rho[1] * chi_minus_one
    if any(
        rho[order - k] != chi_minus_one * point_scale * rho[k]
        for k in range(1, order)
    ):
        raise AssertionError("residue negation scale was not constant")
    rho_kummer = all(rho[order - k] == rho[k] for k in range(1, order))

    raw_signs: dict[str, list[int]] = {}
    nonvanishing: list[int] = []
    for jet, jet_poly in jet_polynomials.items():
        signs: list[int] = []
        for k in range(1, order):
            point = points[k]
            assert point is not None
            value = poly_eval(jet_poly, point[1], p)
            sign = quadratic_character(value, p)
            if sign == 0:
                break
            signs.append(sign)
        else:
            raw_signs[f"J{jet}"] = signs
            nonvanishing.append(jet)

    # Coordinate twists preserve compact evaluability and cover the smallest
    # invariantization choices for ordinary Y-jets.
    augmented: dict[str, list[int]] = dict(raw_signs)
    for name, signs in list(raw_signs.items()):
        augmented[f"{name}*chi_y"] = []
        augmented[f"{name}*chi_x"] = []
        augmented[f"{name}*chi_xy"] = []
        for index, k in enumerate(range(1, order)):
            point = points[k]
            assert point is not None
            x, y = point
            cx = quadratic_character(x, p)
            cy = quadratic_character(y, p)
            augmented[f"{name}*chi_y"].append(signs[index] * cy)
            augmented[f"{name}*chi_x"].append(signs[index] * cx)
            augmented[f"{name}*chi_xy"].append(signs[index] * cx * cy)

    raw_base = {name: bits(signs) for name, signs in augmented.items()}
    raw_vectors = products(raw_base)

    orbit_base: dict[str, int] = {}
    for name, signs in augmented.items():
        orbit_signs = [
            signs[k - 1]
            * signs[(lam * k % order) - 1]
            * signs[(lam2 * k % order) - 1]
            for k in range(1, order)
        ]
        orbit_base[f"N({name})"] = bits(orbit_signs)
    orbit_vectors = products(orbit_base)

    length = order - 1
    complement = (1 << length) - 1
    carry_values = [scalar_carry_sign(k, lam, order) for k in range(1, order)]
    carry_target = bits(carry_values)
    r3_values = [
        rho[k] * rho[lam * k % order] * rho[lam2 * k % order]
        for k in range(1, order)
    ]
    r3_target = bits(r3_values)
    normalized_values = [
        (point_scale if scalar_carry_sign(k, lam, order) == -1 else 1)
        * r3_values[k - 1]
        for k in range(1, order)
    ]
    normalized_target = bits(normalized_values)

    def exact_name(vectors: dict[int, str], target: int) -> str | None:
        if target in vectors:
            return vectors[target]
        if target ^ complement in vectors:
            return "-" + vectors[target ^ complement]
        return None

    exact_carry = exact_name(raw_vectors | orbit_vectors, carry_target)
    exact_r3 = exact_name(raw_vectors | orbit_vectors, r3_target)
    exact_normalized = exact_name(raw_vectors | orbit_vectors, normalized_target)

    all_vectors = dict(raw_vectors)
    all_vectors.update(orbit_vectors)
    carry_observed = best_accuracy(all_vectors, carry_target, length)
    r3_observed = best_accuracy(all_vectors, r3_target, length)

    rng = random.Random(20260812 + 43 * p + order)
    carry_null = sorted(
        best_accuracy(all_vectors, random_anti_c6(order, lam, rng), length)[0]
        for _ in range(NULL_TRIALS)
    )
    carry_q95 = carry_null[math.ceil(0.95 * NULL_TRIALS) - 1]

    if rho_kummer:
        r3_null = sorted(
            best_accuracy(all_vectors, random_kummer_c6(order, lam, rng), length)[0]
            for _ in range(NULL_TRIALS)
        )
        r3_median = statistics.median(r3_null)
        r3_q95 = r3_null[math.ceil(0.95 * NULL_TRIALS) - 1]
        r3_percentile = sum(value <= r3_observed[0] for value in r3_null) / NULL_TRIALS
    else:
        r3_null = []
        r3_median = 0.0
        r3_q95 = 0.0
        r3_percentile = 0.0

    return CaseResult(
        p=p,
        order=order,
        generator=generator,
        beta=beta,
        lam=lam,
        point_scale_character=point_scale,
        rho_kummer_invariant=rho_kummer,
        kernel_polynomial_degree=len(polynomial) - 1,
        nonvanishing_raw_jets=tuple(nonvanishing),
        raw_candidate_vectors=len(raw_vectors),
        orbit_candidate_vectors=len(orbit_vectors),
        exact_carry_decoder=exact_carry,
        exact_r3_decoder=exact_r3,
        exact_normalized_orbit_decoder=exact_normalized,
        best_carry_accuracy=carry_observed[0],
        best_carry_candidate=carry_observed[1],
        carry_null_median=statistics.median(carry_null),
        carry_null_q95=carry_q95,
        carry_empirical_percentile=(
            sum(value <= carry_observed[0] for value in carry_null) / NULL_TRIALS
        ),
        best_r3_accuracy=r3_observed[0],
        best_r3_candidate=r3_observed[1],
        r3_null_median=r3_median,
        r3_null_q95=r3_q95,
        r3_empirical_percentile=r3_percentile,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("frobenius_kernel_jet_results.json"),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    large = [case for case in cases if case.order >= 500]
    payload = {
        "scope": (
            "fifteen frozen j=0 prime-order toy subgroups; "
            "no external point, key, wallet, or production target"
        ),
        "package": "FROBENIUS-KERNEL-JETS-014",
        "compact_map": "pi-1 = Frobenius minus identity",
        "maximum_jet_order": JMAX,
        "maximum_character_product_weight": MAX_PRODUCT_WEIGHT,
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases": len(cases),
            "exact_carry_decoders": sum(case.exact_carry_decoder is not None for case in cases),
            "exact_r3_decoders": sum(case.exact_r3_decoder is not None for case in cases),
            "exact_normalized_orbit_decoders": sum(
                case.exact_normalized_orbit_decoder is not None for case in cases
            ),
            "large_carry_cases_strictly_above_null_q95": sum(
                case.best_carry_accuracy > case.carry_null_q95 for case in large
            ),
            "large_r3_cases_strictly_above_null_q95": sum(
                case.rho_kummer_invariant
                and case.best_r3_accuracy > case.r3_null_q95
                for case in large
            ),
            "largest_order": max(case.order for case in cases),
        },
        "decision_rule": (
            "A positive route requires a cross-order exact identity or repeated "
            "strict exceedance of the matched 95% null envelope on increasing orders."
        ),
        "claim_boundary": [
            "Ordinary Y-jets and simple coordinate twists are a bounded proxy for invariant jets.",
            "A fixed positive jet would still require a literal compact evaluation and exceptional-locus proof.",
            "Failure through jet eight is not a theorem for all Frobenius jets.",
            "No external or production-sized input is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
