#!/usr/bin/env python3
"""Exact frozen certificate for FIELD-PERMUTATION-CARRY-IDENTITY-017.

For canonical representatives

    x0 = [x]_p,
    x1 = [beta*x]_p,
    x2 = [beta^2*x]_p,

define the integer permutation orientation

    O_beta(x) = sign((x0-x1)(x1-x2)(x2-x0)).

Put u = (beta-1)*x. The directed gaps from x0 to x1, x1 to x2,
and x2 to x0 are exactly the canonical GLV orbit of u. Their sum is p
for positive cyclic orientation and 2p for negative orientation. Therefore

    O_beta(x) = -C_beta((beta-1)*x),

where C_beta is the public field GLV carry sign.

The script verifies this identity for every nonzero field element in the frozen
cases, verifies the exact Fourier decimation identity, and records the resulting
logarithmic field-Fourier L1 boundary. It accepts no external curve, point, key,
wallet, or production-sized target.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

SELECTED_GROUP_CANDIDATES = (
    "field_permutation*half_y",
    "field_permutation*chi_y",
    "field_carry_x*field_permutation*half_y",
)
LARGE_ORDER_FLOOR = 500


def harmonic(number: int) -> float:
    return math.fsum(1.0 / value for value in range(1, number + 1))


def field_carry_sign(value: int, beta: int, prime: int) -> int:
    value %= prime
    if value == 0:
        return 0
    first = beta * value % prime
    second = beta * first % prime
    total = value + first + second
    if total == prime:
        return -1
    if total == 2 * prime:
        return 1
    raise AssertionError("canonical field GLV orbit did not sum to p or 2p")


def permutation_orientation(value: int, beta: int, prime: int) -> int:
    value %= prime
    if value == 0:
        return 0
    values = (
        value,
        beta * value % prime,
        beta * beta * value % prime,
    )
    product = (
        (values[0] - values[1])
        * (values[1] - values[2])
        * (values[2] - values[0])
    )
    if product == 0:
        raise AssertionError("nonzero GLV orbit had repeated representatives")
    return 1 if product > 0 else -1


def normalized_fourier(values: np.ndarray) -> np.ndarray:
    return np.fft.fft(values) / len(values)


def circular_convolution(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    size = len(left)
    return np.asarray(
        [
            sum(left[index] * right[(frequency - index) % size] for index in range(size))
            for frequency in range(size)
        ],
        dtype=np.complex128,
    )


def metric_by_name(case: dict[str, Any], name: str) -> dict[str, Any]:
    for metric in case["metrics"]:
        if metric["name"] == name:
            return metric
    raise KeyError(f"missing frozen candidate metric {name!r}")


@dataclass(frozen=True)
class GroupCandidateMetric:
    name: str
    max_nonzero_abs: float
    max_frequency: int
    max_times_sqrt_order: float
    max_times_log_order: float
    coefficient_ge_inverse_log: bool
    conditional_bound: str


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    beta: int
    beta_squared: int
    scale_beta_minus_one: int
    inverse_scale: int
    pointwise_identity_checks: int
    directed_gap_checks: int
    orbit_scaling_checks: int
    fourier_decimation_max_error: float
    field_carry_fourier_l1: float
    field_permutation_fourier_l1: float
    l1_equality_error: float
    harmonic_l1_bound: float
    maximum_field_carry_coefficient: float
    maximum_field_permutation_coefficient: float
    maximum_coefficient_equality_error: float
    field_permutation_principal_minus_one_over_pi: float
    product_convolution_max_error: float
    product_fourier_l1: float
    product_l1_upper_bound: float
    selected_group_metrics: list[GroupCandidateMetric]


def run_case(case: dict[str, Any]) -> CaseResult:
    prime = int(case["p"])
    order = int(case["order"])
    beta = int(case["beta"])
    beta_squared = beta * beta % prime
    if beta in (0, 1) or beta_squared in (0, 1):
        raise AssertionError("degenerate cube root")
    if pow(beta, 3, prime) != 1 or (beta_squared + beta + 1) % prime:
        raise AssertionError("beta failed its Eisenstein polynomial")

    scale = (beta - 1) % prime
    inverse_scale = pow(scale, -1, prime)
    carry = np.zeros(prime, dtype=np.float64)
    orientation = np.zeros(prime, dtype=np.float64)
    checks = 0
    gap_checks = 0
    scaling_checks = 0

    for value in range(1, prime):
        x0 = value
        x1 = beta * value % prime
        x2 = beta_squared * value % prime
        u0 = scale * value % prime
        u1 = beta * u0 % prime
        u2 = beta_squared * u0 % prime

        expected_gaps = (
            (x1 - x0) % prime,
            (x2 - x1) % prime,
            (x0 - x2) % prime,
        )
        if (u0, u1, u2) != expected_gaps:
            raise AssertionError("directed gaps were not the scaled GLV orbit")
        if any(gap == 0 for gap in expected_gaps):
            raise AssertionError("directed gap vanished")
        gap_sum = sum(expected_gaps)
        if gap_sum not in (prime, 2 * prime):
            raise AssertionError("directed gap sum was not p or 2p")

        direct_orientation = permutation_orientation(value, beta, prime)
        gap_orientation = 1 if gap_sum == prime else -1
        if direct_orientation != gap_orientation:
            raise AssertionError("directed gap sum lost cyclic orientation")

        carry_value = field_carry_sign(value, beta, prime)
        scaled_carry = field_carry_sign(u0, beta, prime)
        if direct_orientation != -scaled_carry:
            raise AssertionError("field permutation was not negative scaled carry")

        carry[value] = float(carry_value)
        orientation[value] = float(direct_orientation)
        checks += 1
        gap_checks += 1
        scaling_checks += 3

    carry_transform = normalized_fourier(carry)
    orientation_transform = normalized_fourier(orientation)
    decimation_error = max(
        abs(
            orientation_transform[frequency]
            + carry_transform[frequency * inverse_scale % prime]
        )
        for frequency in range(prime)
    )
    if decimation_error > 1e-10:
        raise AssertionError("field Fourier decimation identity failed")

    carry_l1 = float(np.sum(np.abs(carry_transform)))
    orientation_l1 = float(np.sum(np.abs(orientation_transform)))
    l1_error = abs(carry_l1 - orientation_l1)
    if l1_error > 1e-10:
        raise AssertionError("field Fourier L1 was not preserved by scaling")

    harmonic_bound = 3 * harmonic((prime - 1) // 2)
    if orientation_l1 > harmonic_bound + 1e-9:
        raise AssertionError("field permutation exceeded carry harmonic bound")

    carry_max = float(np.max(np.abs(carry_transform[1:])))
    orientation_max = float(np.max(np.abs(orientation_transform[1:])))
    max_error = abs(carry_max - orientation_max)
    if max_error > 1e-10:
        raise AssertionError("maximum coefficient was not preserved")

    product_values = carry * orientation
    product_transform = normalized_fourier(product_values)
    predicted_product_transform = circular_convolution(
        carry_transform, orientation_transform
    )
    convolution_error = float(
        np.max(np.abs(product_transform - predicted_product_transform))
    )
    if convolution_error > 1e-9:
        raise AssertionError("normalized product-convolution identity failed")
    product_l1 = float(np.sum(np.abs(product_transform)))
    product_bound = carry_l1 * orientation_l1
    if product_l1 > product_bound + 1e-8:
        raise AssertionError("product Fourier L1 convolution bound failed")

    conditional_bounds = {
        "field_permutation*half_y": "O(log(p)^2/sqrt(p))",
        "field_permutation*chi_y": "O(log(p)/sqrt(p))",
        "field_carry_x*field_permutation*half_y": "O(log(p)^3/sqrt(p))",
    }
    inverse_log = 1.0 / math.log(order)
    selected_metrics: list[GroupCandidateMetric] = []
    for name in SELECTED_GROUP_CANDIDATES:
        metric = metric_by_name(case, name)
        maximum = float(metric["max_nonzero_abs"])
        selected_metrics.append(
            GroupCandidateMetric(
                name=name,
                max_nonzero_abs=maximum,
                max_frequency=int(metric["max_frequency"]),
                max_times_sqrt_order=maximum * math.sqrt(order),
                max_times_log_order=maximum * math.log(order),
                coefficient_ge_inverse_log=maximum >= inverse_log,
                conditional_bound=conditional_bounds[name],
            )
        )

    return CaseResult(
        p=prime,
        order=order,
        beta=beta,
        beta_squared=beta_squared,
        scale_beta_minus_one=scale,
        inverse_scale=inverse_scale,
        pointwise_identity_checks=checks,
        directed_gap_checks=gap_checks,
        orbit_scaling_checks=scaling_checks,
        fourier_decimation_max_error=decimation_error,
        field_carry_fourier_l1=carry_l1,
        field_permutation_fourier_l1=orientation_l1,
        l1_equality_error=l1_error,
        harmonic_l1_bound=harmonic_bound,
        maximum_field_carry_coefficient=carry_max,
        maximum_field_permutation_coefficient=orientation_max,
        maximum_coefficient_equality_error=max_error,
        field_permutation_principal_minus_one_over_pi=orientation_max - 1 / math.pi,
        product_convolution_max_error=convolution_error,
        product_fourier_l1=product_l1,
        product_l1_upper_bound=product_bound,
        selected_group_metrics=selected_metrics,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spectral-results", type=Path, required=True)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "field_permutation_carry_identity_results.json"
        ),
    )
    args = parser.parse_args()

    spectral_data = json.loads(args.spectral_results.read_text())
    cases = [run_case(case) for case in spectral_data["cases"]]
    large = [case for case in cases if case.order >= LARGE_ORDER_FLOOR]

    by_name: dict[str, list[GroupCandidateMetric]] = {
        name: [] for name in SELECTED_GROUP_CANDIDATES
    }
    for case in large:
        for metric in case.selected_group_metrics:
            by_name[metric.name].append(metric)

    selected_large_summary = {
        name: {
            "large_cases": len(metrics),
            "cases_ge_inverse_log": sum(
                metric.coefficient_ge_inverse_log for metric in metrics
            ),
            "maximum_coefficient_times_sqrt_order": max(
                metric.max_times_sqrt_order for metric in metrics
            ),
            "largest_order_coefficient": next(
                metric.max_nonzero_abs
                for metric in large[-1].selected_group_metrics
                if metric.name == name
            ),
            "conditional_bound": metrics[0].conditional_bound,
        }
        for name, metrics in by_name.items()
    }

    largest_field = max(cases, key=lambda case: case.p)
    payload = {
        "scope": (
            "fifteen frozen j=0 fields and toy groups only; no external curve, "
            "point, key, wallet, or production-sized target"
        ),
        "package": "FIELD-PERMUTATION-CARRY-IDENTITY-017",
        "exact_identity": "O_beta(x)=-C_beta((beta-1)*x)",
        "directed_gap_orbit": (
            "([beta*x]-[x], [beta^2*x]-[beta*x], [x]-[beta^2*x]) mod p "
            "is the beta-orbit of (beta-1)*x"
        ),
        "fourier_identity": (
            "O_hat(a)=-C_hat(a*(beta-1)^(-1)); scaling only permutes frequencies"
        ),
        "conditional_mixed_y_consequences": {
            "field_permutation*half_y": "O(log(p)^2/sqrt(p))",
            "field_permutation*chi_y": "O(log(p)/sqrt(p))",
            "field_carry_x*field_permutation*half_y": "O(log(p)^3/sqrt(p))",
        },
        "cases": [asdict(case) for case in cases],
        "selected_large_summary": selected_large_summary,
        "aggregate": {
            "cases": len(cases),
            "pointwise_identity_checks": sum(
                case.pointwise_identity_checks for case in cases
            ),
            "directed_gap_checks": sum(case.directed_gap_checks for case in cases),
            "orbit_scaling_checks": sum(
                case.orbit_scaling_checks for case in cases
            ),
            "maximum_fourier_decimation_error": max(
                case.fourier_decimation_max_error for case in cases
            ),
            "maximum_l1_equality_error": max(
                case.l1_equality_error for case in cases
            ),
            "maximum_coefficient_equality_error": max(
                case.maximum_coefficient_equality_error for case in cases
            ),
            "maximum_product_convolution_error": max(
                case.product_convolution_max_error for case in cases
            ),
            "all_selected_large_candidates_below_inverse_log": all(
                not metric.coefficient_ge_inverse_log
                for case in large
                for metric in case.selected_group_metrics
            ),
            "largest_field_prime": largest_field.p,
            "largest_field_permutation_l1": largest_field.field_permutation_fourier_l1,
            "largest_field_permutation_l1_over_log_p": (
                largest_field.field_permutation_fourier_l1
                / math.log(largest_field.p)
            ),
            "largest_field_maximum_coefficient": (
                largest_field.maximum_field_permutation_coefficient
            ),
            "largest_field_maximum_minus_one_over_pi": (
                largest_field.field_permutation_principal_minus_one_over_pi
            ),
        },
        "decision": (
            "The integer field-orbit permutation orientation is exactly a scaled "
            "public field carry, not a new observable class. Its field Fourier L1 "
            "is logarithmic and its mixed-y products inherit the conditional "
            "square-root hybrid-sum barriers from package 016."
        ),
        "remaining_open": [
            "high-field-Fourier-L1 or high-conductor public circuits",
            "order-dependent sections not covered by fixed-conductor sums",
            "a direct public cyclotomic carry or R3 decoder",
            "formalization of the external square-root hybrid-sum theorem",
        ],
        "claim_boundary": [
            "The pointwise identity and field Fourier decimation are exact finite checks.",
            "The harmonic L1 bound is inherited from the exact centered-sawtooth carry decomposition.",
            "The mixed-y complexity conclusions remain conditional on the external hybrid-sum theorem from package 016.",
            "No universal lower bound for arbitrary public predicates or ECDLP algorithms is claimed.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
