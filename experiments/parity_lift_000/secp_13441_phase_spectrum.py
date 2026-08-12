#!/usr/bin/env python3
"""Full-phase spectral audit for SECP-13441-PHASE-SPECTRUM-023.

For the public perfectly-periodic point function Phi and the fixed field factor
13441, define

    f_G(k) = Phi([k]G)^((p-1)/13441) in mu_13441,
    f_Q(t) = Phi([t]Q)^((p-1)/13441), Q=[k]G.

Then f_Q(t)=f_G(t*k), so the hidden multiplier acts by multiplicative
decimation on the scalar-domain function.  A sufficiently heavy additive
Fourier coefficient of the full complex phase would therefore be more useful
than any preselected binary lookup table.

This script measures the normalized scalar Fourier spectrum for deterministic
small powers of the canonical order-13441 phase, verifies decimation and C6
symmetries, and compares the maximum coefficient with a matched random
C6-invariant phase null.  It uses only the frozen toy family and accepts no
external curve, point, key, wallet, or production-sized target.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from sympy import isprime

import secp_13441_character_screen as frozen

PHASE_POWERS = (1, 2, 3, 5, 7, 11, 13, 17)
NULL_TRIALS = 24
LARGE_ORDER_FLOOR = 500
REQUIRED_NULL_EXCEEDANCES = 3


def robust_is_prime(value: int) -> bool:
    return bool(isprime(value))


def phase_sequence(curve: frozen.CurveData, power: int) -> np.ndarray:
    root = np.exp(2j * np.pi / frozen.PHASE_ORDER)
    sequence = np.zeros(curve.order, dtype=np.complex128)
    exponents = (curve.phases.astype(np.int64) * power) % frozen.PHASE_ORDER
    sequence[1:] = np.power(root, exponents)
    return sequence


def normalized_fourier(sequence: np.ndarray) -> np.ndarray:
    return np.fft.fft(sequence) / len(sequence)


def maximum_nonzero(transform: np.ndarray) -> tuple[float, int]:
    magnitudes = np.abs(transform)
    frequency = int(np.argmax(magnitudes[1:])) + 1
    return float(magnitudes[frequency]), frequency


def random_c6_phase_sequence(
    curve: frozen.CurveData, rng: np.random.Generator
) -> np.ndarray:
    orbit_phases = rng.integers(
        0, frozen.PHASE_ORDER, size=curve.orbit_count, dtype=np.int64
    )
    exponents = orbit_phases[curve.orbit_ids]
    root = np.exp(2j * np.pi / frozen.PHASE_ORDER)
    sequence = np.zeros(curve.order, dtype=np.complex128)
    sequence[1:] = np.power(root, exponents)
    return sequence


def symmetry_error(
    transform: np.ndarray, order: int, lam: int
) -> tuple[float, float]:
    frequencies = np.arange(order, dtype=np.int64)
    lam_squared = lam * lam % order
    glv_error = float(
        max(
            np.max(np.abs(transform - transform[(lam * frequencies) % order])),
            np.max(
                np.abs(transform - transform[(lam_squared * frequencies) % order])
            ),
        )
    )
    negation_error = float(
        np.max(np.abs(transform - transform[(-frequencies) % order]))
    )
    return glv_error, negation_error


def decimation_error(
    sequence: np.ndarray, transform: np.ndarray, hidden: int
) -> float:
    order = len(sequence)
    scalars = np.arange(order, dtype=np.int64)
    decimated = sequence[(hidden * scalars) % order]
    decimated_transform = normalized_fourier(decimated)
    hidden_inverse = pow(hidden, -1, order)
    expected = transform[(hidden_inverse * scalars) % order]
    return float(np.max(np.abs(decimated_transform - expected)))


@dataclass(frozen=True)
class PowerSpectrum:
    power: int
    maximum_nonzero_coefficient: float
    maximum_frequency: int
    fourier_l1: float
    coefficient_times_sqrt_order: float
    coefficient_times_log_order: float
    coefficient_times_log_squared_order: float
    above_inverse_log: bool
    above_inverse_log_squared: bool
    null_median_maximum: float
    null_q95_maximum: float
    empirical_null_percentile: float
    strictly_above_null_q95: bool
    glv_orbit_max_error: float
    negation_max_error: float
    decimation_max_error: float


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    generator: tuple[int, int]
    lam: int
    point_scale_character: int
    phase_bins_seen: int
    orbit_count: int
    null_trials: int
    null_median_maximum: float
    null_q95_maximum: float
    powers: list[PowerSpectrum]


def run_case(
    curve: frozen.CurveData, rng: np.random.Generator
) -> CaseResult:
    null_maxima: list[float] = []
    if curve.order >= LARGE_ORDER_FLOOR:
        for _ in range(NULL_TRIALS):
            random_sequence = random_c6_phase_sequence(curve, rng)
            random_transform = normalized_fourier(random_sequence)
            maximum, _ = maximum_nonzero(random_transform)
            null_maxima.append(maximum)
    else:
        null_maxima = [0.0]
    null_maxima.sort()
    null_median = float(np.median(null_maxima))
    null_q95 = null_maxima[math.ceil(0.95 * len(null_maxima)) - 1]

    power_results: list[PowerSpectrum] = []
    for power in PHASE_POWERS:
        sequence = phase_sequence(curve, power)
        transform = normalized_fourier(sequence)
        maximum, frequency = maximum_nonzero(transform)
        glv_error, negation_error = symmetry_error(
            transform, curve.order, curve.lam
        )
        hidden = 2 if curve.order != 2 else 1
        decimation = decimation_error(sequence, transform, hidden)
        if glv_error > 1e-9:
            raise AssertionError("phase Fourier spectrum lost GLV symmetry")
        if negation_error > 1e-9:
            raise AssertionError("phase Fourier spectrum lost negation symmetry")
        if decimation > 1e-9:
            raise AssertionError("phase Fourier decimation identity failed")

        inverse_log = 1.0 / math.log(curve.order)
        inverse_log_squared = inverse_log * inverse_log
        percentile = (
            sum(value <= maximum for value in null_maxima) / len(null_maxima)
            if curve.order >= LARGE_ORDER_FLOOR
            else 0.0
        )
        power_results.append(
            PowerSpectrum(
                power=power,
                maximum_nonzero_coefficient=maximum,
                maximum_frequency=frequency,
                fourier_l1=float(np.sum(np.abs(transform))),
                coefficient_times_sqrt_order=maximum * math.sqrt(curve.order),
                coefficient_times_log_order=maximum * math.log(curve.order),
                coefficient_times_log_squared_order=(
                    maximum * math.log(curve.order) ** 2
                ),
                above_inverse_log=maximum >= inverse_log,
                above_inverse_log_squared=maximum >= inverse_log_squared,
                null_median_maximum=null_median,
                null_q95_maximum=null_q95,
                empirical_null_percentile=percentile,
                strictly_above_null_q95=(
                    curve.order >= LARGE_ORDER_FLOOR and maximum > null_q95
                ),
                glv_orbit_max_error=glv_error,
                negation_max_error=negation_error,
                decimation_max_error=decimation,
            )
        )

    return CaseResult(
        p=curve.p,
        order=curve.order,
        generator=curve.generator,
        lam=curve.lam,
        point_scale_character=curve.point_scale_character,
        phase_bins_seen=curve.phase_bins_seen,
        orbit_count=curve.orbit_count,
        null_trials=(NULL_TRIALS if curve.order >= LARGE_ORDER_FLOOR else 0),
        null_median_maximum=null_median,
        null_q95_maximum=null_q95,
        powers=power_results,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "secp_13441_phase_spectrum_results.json"
        ),
    )
    args = parser.parse_args()

    frozen.is_prime = robust_is_prime
    curves = sorted(
        [frozen.build_case(*case) for case in frozen.FROZEN_CASES],
        key=lambda curve: curve.order,
    )
    results = [
        run_case(curve, np.random.default_rng(20260812 + curve.p))
        for curve in curves
    ]
    large = [case for case in results if case.order >= LARGE_ORDER_FLOOR]

    power_summary: dict[str, dict[str, object]] = {}
    admitted_powers: list[int] = []
    for power in PHASE_POWERS:
        rows = [
            next(item for item in case.powers if item.power == power)
            for case in large
        ]
        rows_by_order = sorted(
            zip((case.order for case in large), rows), key=lambda pair: pair[0]
        )
        exceedances = sum(row.strictly_above_null_q95 for row in rows)
        largest_two = rows_by_order[-2:]
        largest_two_invlog2 = all(
            row.above_inverse_log_squared for _, row in largest_two
        )
        admitted = (
            exceedances >= REQUIRED_NULL_EXCEEDANCES
            and largest_two_invlog2
        )
        if admitted:
            admitted_powers.append(power)
        power_summary[str(power)] = {
            "large_cases": len(rows),
            "null_q95_exceedances": exceedances,
            "cases_above_inverse_log": sum(row.above_inverse_log for row in rows),
            "cases_above_inverse_log_squared": sum(
                row.above_inverse_log_squared for row in rows
            ),
            "largest_order_coefficient": largest_two[-1][1].maximum_nonzero_coefficient,
            "largest_order_null_q95": largest_two[-1][1].null_q95_maximum,
            "largest_two_above_inverse_log_squared": largest_two_invlog2,
            "maximum_coefficient_times_sqrt_order": max(
                row.coefficient_times_sqrt_order for row in rows
            ),
            "minimum_coefficient_times_sqrt_order": min(
                row.coefficient_times_sqrt_order for row in rows
            ),
            "admitted_signal": admitted,
        }

    payload = {
        "scope": (
            "sixteen frozen j=0 toy subgroups with 13441 dividing p-1; "
            "full complex public phase and eight deterministic phase powers; "
            "no external point, key, wallet, or production target"
        ),
        "package": "SECP-13441-PHASE-SPECTRUM-023",
        "public_decimation_identity": (
            "for Q=[k]G, f_Q(t)=f_G(t*k), so "
            "Fourier(f_Q)(j)=Fourier(f_G)(j*k^(-1))"
        ),
        "phase_order": frozen.PHASE_ORDER,
        "tested_powers": list(PHASE_POWERS),
        "large_order_floor": LARGE_ORDER_FLOOR,
        "null_trials_per_large_case": NULL_TRIALS,
        "cases": [asdict(case) for case in results],
        "power_summary": power_summary,
        "aggregate": {
            "cases": len(results),
            "large_cases": len(large),
            "admitted_powers": admitted_powers,
            "maximum_glv_symmetry_error": max(
                item.glv_orbit_max_error
                for case in results
                for item in case.powers
            ),
            "maximum_negation_symmetry_error": max(
                item.negation_max_error
                for case in results
                for item in case.powers
            ),
            "maximum_decimation_error": max(
                item.decimation_max_error
                for case in results
                for item in case.powers
            ),
            "largest_subgroup_order": max(case.order for case in results),
        },
        "acceptance_rule": (
            "the same deterministic phase power must exceed its matched C6-null "
            "95% envelope on at least three large curves and remain above "
            "1/log(n)^2 on both largest subgroup orders"
        ),
        "decision": (
            "No tested full-phase power supplies an admitted heavy spectrum."
            if not admitted_powers
            else "At least one full-phase power requires manual local-SFT review."
        ),
        "claim_boundary": [
            "The decimation identity and finite Fourier symmetries are exact up to numerical FFT tolerance.",
            "Only eight deterministic powers of the order-13441 phase are tested, not all 13440 nontrivial powers.",
            "A negative frozen spectrum is not an asymptotic lower bound for the full phase or the remaining secp field cofactor.",
            "No external or production-sized input is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
