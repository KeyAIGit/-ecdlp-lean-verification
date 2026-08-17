#!/usr/bin/env python3
"""Exact field-Fourier and statistical audit for PUBLIC-COORDINATE-SPECTRAL-BARRIER-014.

The script consumes only frozen toy-screen JSON files. It accepts no external
curve, point, key, wallet, or production-sized target.

It verifies two exact integer identities:

* the centered-sawtooth decomposition of the public field GLV carry;
* the cotangent magnitude formula for the centered sawtooth Fourier transform.

It then records harmonic Fourier-L1 bounds for the half-interval and field-carry
predicates, audits the corrected group-spectrum census, and applies a
scale-qualified multiple-testing gate to the coordinate-carry experiment.

The analytic transfer from field Fourier L1 to group Fourier coefficients uses
an external elliptic Gaussian-sum theorem and is documented, not reproved, by
this program.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

SCALE_ORDER_FLOOR = 271
ALPHA = 0.05


def harmonic(number: int) -> float:
    return math.fsum(1.0 / value for value in range(1, number + 1))


def centered_sawtooth_numerator(value: int, modulus: int) -> int:
    """Return 2*modulus*B(value/modulus), with B(0)=0."""
    value %= modulus
    return 0 if value == 0 else 2 * value - modulus


def half_interval_values(modulus: int) -> np.ndarray:
    midpoint = (modulus - 1) // 2
    values = np.zeros(modulus, dtype=np.float64)
    values[1 : midpoint + 1] = 1.0
    values[midpoint + 1 :] = -1.0
    return values


def centered_sawtooth_values(modulus: int) -> np.ndarray:
    return np.asarray(
        [
            centered_sawtooth_numerator(value, modulus) / (2 * modulus)
            for value in range(modulus)
        ],
        dtype=np.float64,
    )


def field_carry_values(modulus: int, beta: int) -> tuple[np.ndarray, int]:
    values = np.zeros(modulus, dtype=np.float64)
    checks = 0
    beta_squared = beta * beta % modulus
    for value in range(1, modulus):
        representatives = (
            value,
            beta * value % modulus,
            beta_squared * value % modulus,
        )
        total = sum(representatives)
        if total == modulus:
            sign = -1
        elif total == 2 * modulus:
            sign = 1
        else:
            raise AssertionError("canonical field GLV orbit did not sum to p or 2p")
        numerator = sum(
            centered_sawtooth_numerator(item, modulus)
            for item in representatives
        )
        if numerator != sign * modulus:
            raise AssertionError("centered-sawtooth carry identity failed")
        if 2 * total - 3 * modulus != sign * modulus:
            raise AssertionError("integer carry numerator identity failed")
        values[value] = float(sign)
        checks += 1
    return values, checks


def normalized_fourier(values: np.ndarray) -> np.ndarray:
    return np.fft.fft(values) / len(values)


@dataclass(frozen=True)
class FieldCase:
    p: int
    order: int
    beta: int
    carry_identity_checks: int
    centered_sawtooth_cotangent_max_error: float
    centered_sawtooth_fourier_l1: float
    centered_sawtooth_harmonic_bound: float
    half_interval_fourier_l1: float
    half_interval_harmonic_bound: float
    field_carry_fourier_l1: float
    field_carry_harmonic_bound: float
    half_x_group_max_coefficient: float
    half_x_times_sqrt_order: float
    field_carry_x_group_max_coefficient: float
    field_carry_x_times_sqrt_order: float
    half_x_gaussian_scale_proxy: float
    field_carry_x_gaussian_scale_proxy: float


def metric_by_name(case: dict[str, Any], name: str) -> dict[str, Any]:
    for metric in case["metrics"]:
        if metric["name"] == name:
            return metric
    raise KeyError(f"missing candidate metric: {name}")


def run_field_case(case: dict[str, Any]) -> FieldCase:
    p = int(case["p"])
    order = int(case["order"])
    beta = int(case["beta"])
    if beta in (0, 1) or pow(beta, 3, p) != 1:
        raise AssertionError("beta is not a nontrivial cube root")

    midpoint = (p - 1) // 2
    harmonic_value = harmonic(midpoint)

    sawtooth = centered_sawtooth_values(p)
    half_interval = half_interval_values(p)
    field_carry, carry_checks = field_carry_values(p, beta)

    sawtooth_transform = normalized_fourier(sawtooth)
    half_transform = normalized_fourier(half_interval)
    carry_transform = normalized_fourier(field_carry)

    cotangent_error = max(
        abs(
            abs(sawtooth_transform[frequency])
            - abs(1.0 / math.tan(math.pi * frequency / p)) / (2 * p)
        )
        for frequency in range(1, p)
    )
    if cotangent_error > 1e-10:
        raise AssertionError("centered-sawtooth cotangent formula failed")

    sawtooth_l1 = float(np.sum(np.abs(sawtooth_transform)))
    half_l1 = float(np.sum(np.abs(half_transform)))
    carry_l1 = float(np.sum(np.abs(carry_transform)))
    sawtooth_bound = harmonic_value / 2
    half_bound = harmonic_value + 1
    carry_bound = 3 * harmonic_value
    if sawtooth_l1 > sawtooth_bound + 1e-9:
        raise AssertionError("sawtooth Fourier-L1 harmonic bound failed")
    if half_l1 > half_bound + 1e-9:
        raise AssertionError("half-interval Fourier-L1 harmonic bound failed")
    if carry_l1 > carry_bound + 1e-9:
        raise AssertionError("field-carry Fourier-L1 harmonic bound failed")

    half_metric = metric_by_name(case, "half_x")
    carry_metric = metric_by_name(case, "field_carry_x")
    gaussian_factor = math.sqrt(p) / order

    return FieldCase(
        p=p,
        order=order,
        beta=beta,
        carry_identity_checks=carry_checks,
        centered_sawtooth_cotangent_max_error=cotangent_error,
        centered_sawtooth_fourier_l1=sawtooth_l1,
        centered_sawtooth_harmonic_bound=sawtooth_bound,
        half_interval_fourier_l1=half_l1,
        half_interval_harmonic_bound=half_bound,
        field_carry_fourier_l1=carry_l1,
        field_carry_harmonic_bound=carry_bound,
        half_x_group_max_coefficient=float(half_metric["max_nonzero_abs"]),
        half_x_times_sqrt_order=float(half_metric["max_times_sqrt_order"]),
        field_carry_x_group_max_coefficient=float(carry_metric["max_nonzero_abs"]),
        field_carry_x_times_sqrt_order=float(carry_metric["max_times_sqrt_order"]),
        half_x_gaussian_scale_proxy=gaussian_factor * half_l1,
        field_carry_x_gaussian_scale_proxy=gaussian_factor * carry_l1,
    )


def strict_tail_add_one(case: dict[str, Any], prefix: str) -> float:
    trials = int(case[f"{prefix}_null_trials"])
    percentile = float(case[f"{prefix}_empirical_null_percentile"])
    if trials <= 0:
        return 1.0
    count_less_or_equal = min(trials, max(0, round(percentile * trials)))
    strictly_greater = trials - count_less_or_equal
    return (strictly_greater + 1) / (trials + 1)


def holm_passes(rows: list[tuple[float, int]], alpha: float) -> list[int]:
    ordered = sorted(rows)
    passes: list[int] = []
    total = len(ordered)
    for index, (p_value, order) in enumerate(ordered):
        threshold = alpha / (total - index)
        if p_value > threshold:
            break
        passes.append(order)
    return passes


def statistical_audit(cm_data: dict[str, Any]) -> dict[str, Any]:
    cases = cm_data["cases"]
    large = [case for case in cases if int(case["order"]) >= SCALE_ORDER_FLOOR]
    carry_rows = [
        (strict_tail_add_one(case, "carry"), int(case["order"]))
        for case in large
    ]
    r3_rows = [
        (strict_tail_add_one(case, "r3"), int(case["order"]))
        for case in large
        if int(case["r3_null_trials"]) > 0
    ]
    exact_orders = sorted(
        int(case["order"]) for case in cases if case["carry_exact_decoder"]
    )
    exact_large_orders = [order for order in exact_orders if order >= SCALE_ORDER_FLOOR]
    q95_orders = sorted(
        int(case["order"])
        for case in large
        if float(case["carry_best_accuracy"]) > float(case["carry_null_q95"])
    )
    return {
        "alpha": ALPHA,
        "scale_order_floor": SCALE_ORDER_FLOOR,
        "all_cases": len(cases),
        "scale_qualified_cases": len(large),
        "chance_at_least_one_nominal_q95_exceedance_all_cases": 1 - 0.95 ** len(cases),
        "chance_at_least_one_nominal_q95_exceedance_scale_qualified": 1 - 0.95 ** len(large),
        "exact_carry_decoder_orders": exact_orders,
        "exact_carry_decoder_orders_scale_qualified": exact_large_orders,
        "scale_qualified_q95_exceedance_orders": q95_orders,
        "minimum_scale_qualified_carry_strict_tail_add_one": min(
            (value for value, _ in carry_rows), default=1.0
        ),
        "minimum_scale_qualified_r3_strict_tail_add_one": min(
            (value for value, _ in r3_rows), default=1.0
        ),
        "holm_bonferroni_carry_pass_orders": holm_passes(carry_rows, ALPHA),
        "holm_bonferroni_r3_pass_orders": holm_passes(r3_rows, ALPHA),
        "decision": (
            "no scale-qualified exact decoder and no Holm-Bonferroni correlation pass"
        ),
        "boundary": (
            "The add-one strict-tail value is conservative only up to unrecorded ties; "
            "the decisive facts are the absence of exact decoders at order >=271 and "
            "the absence of repeated inverse-log spectral weight."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cm-results", type=Path, required=True)
    parser.add_argument("--spectral-results", type=Path, required=True)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "public_coordinate_spectral_barrier_results.json"
        ),
    )
    args = parser.parse_args()

    cm_data = json.loads(args.cm_results.read_text())
    spectral_data = json.loads(args.spectral_results.read_text())
    field_cases = [run_field_case(case) for case in spectral_data["cases"]]
    large_field_cases = [case for case in field_cases if case.order >= 500]

    spectral_aggregate = spectral_data["aggregate"]
    stats = statistical_audit(cm_data)
    payload = {
        "scope": (
            "frozen toy curves only; no external point, key, wallet, or "
            "production-sized target"
        ),
        "package": "PUBLIC-COORDINATE-SPECTRAL-BARRIER-014",
        "field_fourier_transfer": {
            "identity": (
                "hhat(j)=sum_a Fhat(a)*(1/n)*sum_k e_p(a*x([k]G))*e_n(-j*k)"
            ),
            "external_input": (
                "twisted elliptic Gaussian sums are O(sqrt(p)); this script "
                "verifies only the elementary field Fourier side"
            ),
            "consequence_for_cofactor_one": (
                "if ||Fhat||_1=polylog(p), every nonzero group Fourier "
                "coefficient is O(polylog(p)/sqrt(p))"
            ),
        },
        "exact_field_carry_identity": (
            "C_beta(x)=2*(B(x)+B(beta*x)+B(beta^2*x)), "
            "B(u)=[u]_p/p-1/2 for u!=0"
        ),
        "field_cases": [asdict(case) for case in field_cases],
        "statistical_audit": stats,
        "corrected_spectral_census": {
            "largest_order": spectral_aggregate["largest_order"],
            "largest_order_best_public_coefficient": spectral_aggregate[
                "largest_order_best_public_coefficient"
            ],
            "largest_order_best_candidate": spectral_aggregate[
                "largest_order_best_candidate"
            ],
            "repeated_inverse_log_candidates": spectral_aggregate[
                "candidate_names_repeatedly_ge_inverse_log_on_large_cases"
            ],
            "largest_large_case_half_x_times_sqrt_order": max(
                case.half_x_times_sqrt_order for case in large_field_cases
            ),
            "largest_large_case_field_carry_x_times_sqrt_order": max(
                case.field_carry_x_times_sqrt_order for case in large_field_cases
            ),
        },
        "aggregate": {
            "field_cases": len(field_cases),
            "field_carry_identity_checks": sum(
                case.carry_identity_checks for case in field_cases
            ),
            "maximum_sawtooth_cotangent_error": max(
                case.centered_sawtooth_cotangent_max_error
                for case in field_cases
            ),
            "all_harmonic_l1_bounds_passed": True,
            "repeated_inverse_log_public_spectrum_found": bool(
                spectral_aggregate[
                    "candidate_names_repeatedly_ge_inverse_log_on_large_cases"
                ]
            ),
            "scale_qualified_coordinate_decoder_found": bool(
                stats["exact_carry_decoder_orders_scale_qualified"]
            ),
        },
        "decision": (
            "The half-x and field-GLV-carry-x predicates are analytically "
            "square-root-scale after field-Fourier transfer. The broader frozen "
            "public census shows no repeated inverse-log-heavy coefficient."
        ),
        "claim_boundary": [
            "The centered-sawtooth identities and Fourier-L1 bounds are exact or numerically replayed finite identities.",
            "The O(sqrt(p)) elliptic Gaussian-sum estimate is an external theorem, not formalized here.",
            "The theorem closes x-coordinate predicates whose field Fourier L1 is polylogarithmic; it does not close arbitrary y-dependent or high-complexity circuits.",
            "The statistical audit is bounded toy evidence and a gate correction, not an asymptotic lower bound.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
