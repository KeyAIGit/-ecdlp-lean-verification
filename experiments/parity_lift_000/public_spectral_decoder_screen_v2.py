#!/usr/bin/env python3
"""Normalization-aware toy spectral census for public DLP observables.

For a public point predicate h and Q=[k]G,

    h_Q(t)=h([t]Q)=h_G(t*k mod n).

Hence the additive spectrum is multiplicatively decimated by the hidden scalar.
A stable inverse-polylogarithmic nonzero Fourier coefficient would support a
classical local-SFT recovery route.

The perfectly-periodic point-function character is replayed as

    C_G(k)=s^k*rho_G(k),

where the public point-scale character s is derived from the residue negation
law.  This corrects the secp-specific s=-1 specialization in the first census.
No external curve, point, key, wallet, or production-sized target is accepted.
"""
from __future__ import annotations

import argparse
import json
import math
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

SMALL_INDICES = (2, 3, 4, 5, 7, 8, 11, 13)


def half_sign(value: int, modulus: int) -> int:
    value %= modulus
    if value == 0:
        return 0
    return 1 if 2 * value < modulus else -1


def field_carry_sign(x: int, beta: int, p: int) -> int:
    x0 = x % p
    x1 = beta * x0 % p
    x2 = beta * x1 % p
    total = x0 + x1 + x2
    if total == p:
        return -1
    if total == 2 * p:
        return 1
    raise AssertionError("field GLV carry failed")


def permutation_orientation(values: tuple[int, int, int]) -> int:
    x0, x1, x2 = values
    product = (x0 - x1) * (x1 - x2) * (x2 - x0)
    if product == 0:
        return 0
    return 1 if product > 0 else -1


def spectrum_metrics(values: list[int]) -> dict[str, float | int]:
    vector = np.asarray(values, dtype=np.float64)
    transform = np.fft.fft(vector) / len(vector)
    magnitudes = np.abs(transform)
    magnitudes[0] = 0.0
    frequency = int(np.argmax(magnitudes))
    maximum = float(magnitudes[frequency])
    return {
        "max_nonzero_abs": maximum,
        "max_frequency": frequency,
        "fourier_l1": float(np.sum(magnitudes)),
        "coefficients_ge_0_25": int(np.sum(magnitudes >= 0.25)),
        "coefficients_ge_0_10": int(np.sum(magnitudes >= 0.10)),
        "coefficients_ge_inverse_log": int(
            np.sum(magnitudes >= 1 / math.log(len(values)))
        ),
    }


@dataclass(frozen=True)
class CandidateMetric:
    name: str
    max_nonzero_abs: float
    max_frequency: int
    fourier_l1: float
    coefficients_ge_0_25: int
    coefficients_ge_0_10: int
    coefficients_ge_inverse_log: int
    max_times_sqrt_order: float
    max_times_log_order: float


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    generator: tuple[int, int]
    beta: int
    lam: int
    point_scale_character: int
    rho_kummer_invariant: bool
    candidate_count: int
    best_candidate: str
    best_max_nonzero_abs: float
    best_frequency: int
    best_times_sqrt_order: float
    best_times_log_order: float
    candidates_ge_0_10: int
    candidates_ge_inverse_log: int
    metrics: tuple[CandidateMetric, ...]


def run_case(p: int, order: int, generator: tuple[int, int]) -> CaseResult:
    points = orbit(generator, order, p)
    beta = primitive_cube_root(p)
    point_to_scalar = {point: scalar for scalar, point in enumerate(points)}
    lam = point_to_scalar[(beta * generator[0] % p, generator[1])]
    lam2 = lam * lam % order

    psi_g = division_polynomial_evaluator(generator, p)
    rho = [0] + [quadratic_character(psi_g(k), p) for k in range(1, order)]
    if any(value not in (-1, 1) for value in rho[1:]):
        raise AssertionError("EDS residue vanished")

    chi_minus_one = quadratic_character(-1, p)
    point_scale = rho[order - 1] * rho[1] * chi_minus_one
    if point_scale not in (-1, 1):
        raise AssertionError("point-scale character was not binary")
    if any(
        rho[order - k] != chi_minus_one * point_scale * rho[k]
        for k in range(1, order)
    ):
        raise AssertionError("residue negation law did not have a fixed scale")
    rho_kummer = all(rho[order - k] == rho[k] for k in range(1, order))

    names = [
        "chi_x",
        "chi_y",
        "chi_xy",
        "half_x",
        "half_y",
        "field_carry_x",
        "field_carry_x*half_y",
        "field_carry_x*chi_y",
        "field_permutation*half_y",
        "field_permutation*chi_y",
        "field_carry_x*field_permutation*half_y",
        "public_point_function_character",
        "public_C3_orbit_norm",
    ]
    candidates: dict[str, list[int]] = {name: [0] * order for name in names}
    for index in SMALL_INDICES:
        if index < order:
            candidates[f"chi_psi_{index}"] = [0] * order
            candidates[f"chi_psi_{index}_C3"] = [0] * order

    for k in range(1, order):
        point = points[k]
        assert point is not None
        x, y = point
        x1 = beta * x % p
        x2 = beta * x1 % p
        fc = field_carry_sign(x, beta, p)
        po = permutation_orientation((x, x1, x2))
        hx = half_sign(x, p)
        hy = half_sign(y, p)
        cx = quadratic_character(x, p)
        cy = quadratic_character(y, p)

        candidates["chi_x"][k] = cx
        candidates["chi_y"][k] = cy
        candidates["chi_xy"][k] = cx * cy
        candidates["half_x"][k] = hx
        candidates["half_y"][k] = hy
        candidates["field_carry_x"][k] = fc
        candidates["field_carry_x*half_y"][k] = fc * hy
        candidates["field_carry_x*chi_y"][k] = fc * cy
        candidates["field_permutation*half_y"][k] = po * hy
        candidates["field_permutation*chi_y"][k] = po * cy
        candidates["field_carry_x*field_permutation*half_y"][k] = fc * po * hy
        candidates["public_point_function_character"][k] = (
            (point_scale if k & 1 else 1) * rho[k]
        )

        psi_point = division_polynomial_evaluator(point, p)
        for index in SMALL_INDICES:
            if index >= order:
                continue
            value = quadratic_character(psi_point(index), p)
            if value == 0:
                raise AssertionError("fixed-index division section vanished")
            candidates[f"chi_psi_{index}"][k] = value

    for k in range(1, order):
        k1 = lam * k % order
        k2 = lam2 * k % order
        candidates["public_C3_orbit_norm"][k] = (
            candidates["public_point_function_character"][k]
            * candidates["public_point_function_character"][k1]
            * candidates["public_point_function_character"][k2]
        )

    for index in SMALL_INDICES:
        name = f"chi_psi_{index}"
        orbit_name = f"chi_psi_{index}_C3"
        if name not in candidates:
            continue
        for k in range(1, order):
            candidates[orbit_name][k] = (
                candidates[name][k]
                * candidates[name][lam * k % order]
                * candidates[name][lam2 * k % order]
            )

    metrics: list[CandidateMetric] = []
    log_order = math.log(order)
    for name, values in sorted(candidates.items()):
        raw = spectrum_metrics(values)
        maximum = float(raw["max_nonzero_abs"])
        metrics.append(
            CandidateMetric(
                name=name,
                max_nonzero_abs=maximum,
                max_frequency=int(raw["max_frequency"]),
                fourier_l1=float(raw["fourier_l1"]),
                coefficients_ge_0_25=int(raw["coefficients_ge_0_25"]),
                coefficients_ge_0_10=int(raw["coefficients_ge_0_10"]),
                coefficients_ge_inverse_log=int(raw["coefficients_ge_inverse_log"]),
                max_times_sqrt_order=maximum * math.sqrt(order),
                max_times_log_order=maximum * log_order,
            )
        )

    best = max(metrics, key=lambda row: (row.max_nonzero_abs, row.name))
    inverse_log = 1 / log_order
    return CaseResult(
        p=p,
        order=order,
        generator=generator,
        beta=beta,
        lam=lam,
        point_scale_character=point_scale,
        rho_kummer_invariant=rho_kummer,
        candidate_count=len(metrics),
        best_candidate=best.name,
        best_max_nonzero_abs=best.max_nonzero_abs,
        best_frequency=best.max_frequency,
        best_times_sqrt_order=best.max_times_sqrt_order,
        best_times_log_order=best.max_times_log_order,
        candidates_ge_0_10=sum(row.max_nonzero_abs >= 0.10 for row in metrics),
        candidates_ge_inverse_log=sum(
            row.max_nonzero_abs >= inverse_log for row in metrics
        ),
        metrics=tuple(metrics),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("public_spectral_decoder_v2_results.json"),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    large = [case for case in cases if case.order >= 500]

    by_name: dict[str, list[tuple[int, float, float, float]]] = {}
    for case in cases:
        for metric in case.metrics:
            by_name.setdefault(metric.name, []).append(
                (
                    case.order,
                    metric.max_nonzero_abs,
                    metric.max_times_sqrt_order,
                    metric.max_times_log_order,
                )
            )

    repeated_large_ge_0_10 = []
    repeated_large_ge_inverse_log = []
    for name, rows in by_name.items():
        large_rows = [row for row in rows if row[0] >= 500]
        if sum(maximum >= 0.10 for _, maximum, _, _ in large_rows) >= 2:
            repeated_large_ge_0_10.append(name)
        if sum(
            maximum >= 1 / math.log(order)
            for order, maximum, _, _ in large_rows
        ) >= 2:
            repeated_large_ge_inverse_log.append(name)

    largest_case = max(cases, key=lambda row: row.order)
    payload = {
        "scope": (
            "fifteen frozen j=0 prime-order toy subgroups; "
            "no external point, key, wallet, or production target"
        ),
        "package": "PUBLIC-SPECTRAL-DECODER-011-V2",
        "decimation_identity": "h_Q(t)=h_G(t*k mod n)",
        "point_function_character": "C_G(k)=s^k*rho_G(k)",
        "acceptance_target": (
            "the same public candidate retains a nonzero Fourier coefficient "
            "at least inverse-polynomial in log(n) on increasing orders"
        ),
        "cases": [asdict(case) for case in cases],
        "cross_order": {
            name: [
                {
                    "order": order,
                    "max_nonzero_abs": maximum,
                    "max_times_sqrt_order": scaled_sqrt,
                    "max_times_log_order": scaled_log,
                }
                for order, maximum, scaled_sqrt, scaled_log in sorted(rows)
            ]
            for name, rows in sorted(by_name.items())
        },
        "aggregate": {
            "cases": len(cases),
            "large_cases": len(large),
            "largest_order": largest_case.order,
            "point_scale_minus_one_cases": sum(
                case.point_scale_character == -1 for case in cases
            ),
            "kummer_residue_cases": sum(case.rho_kummer_invariant for case in cases),
            "large_cases_with_any_candidate_ge_0_10": sum(
                case.candidates_ge_0_10 > 0 for case in large
            ),
            "large_cases_with_any_candidate_ge_inverse_log": sum(
                case.candidates_ge_inverse_log > 0 for case in large
            ),
            "candidate_names_repeatedly_ge_0_10_on_large_cases": repeated_large_ge_0_10,
            "candidate_names_repeatedly_ge_inverse_log_on_large_cases": repeated_large_ge_inverse_log,
            "largest_observed_public_coefficient": max(
                case.best_max_nonzero_abs for case in cases
            ),
            "largest_order_best_public_coefficient": largest_case.best_max_nonzero_abs,
            "largest_order_best_candidate": largest_case.best_candidate,
        },
        "benchmarks": {
            "scalar_parity_principal_coefficient": "asymptotic 2/pi",
            "GLV_carry_principal_coefficient": "asymptotic 1/pi",
            "square_root_scale": "constant/sqrt(n)",
        },
        "claim_boundary": [
            "A toy heavy coefficient is only a candidate; public evaluation and a literal local-SFT proof remain required.",
            "Failure of this finite census is not a lower bound for all public predicates.",
            "The point-function sequence is replayed through its normalization-aware character identity.",
            "No external or production-sized input is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
