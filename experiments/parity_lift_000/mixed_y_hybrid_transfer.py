#!/usr/bin/env python3
"""Frozen audit for MIXED-Y-HYBRID-TRANSFER-016.

The script accepts only the normalization-aware public spectral census JSON.
It never accepts an external curve, point, key, wallet, or production-sized
target.

Exact finite checks:
  * additive Fourier L1 of the centered half-interval predicate;
  * quadratic-character Gauss-spectrum magnitudes;
  * public field-GLV-carry centered-sawtooth decomposition and L1 bound;
  * tensor-product L1 identities for carry(x)*half(y) and carry(x)*chi(y);
  * scalar-domain Fourier scaling already measured by the frozen census.

Analytic boundary:
  * half_y and carry_x*half_y require complete additive hybrid sums for
    f(P)=a*x(P)+b*y(P);
  * chi_y and carry_x*chi_y require Kummer or additive-Kummer hybrid sums;
  * the required O(sqrt(p)) estimates are external theorem inputs and are not
    proved by this script.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

LARGE_ORDER_FLOOR = 500
SELECTED_CANDIDATES = (
    "half_y",
    "chi_y",
    "field_carry_x*half_y",
    "field_carry_x*chi_y",
)


def harmonic(number: int) -> float:
    return math.fsum(1.0 / value for value in range(1, number + 1))


def normalized_fourier(values: np.ndarray) -> np.ndarray:
    return np.fft.fft(values) / len(values)


def quadratic_character(value: int, prime: int) -> int:
    value %= prime
    if value == 0:
        return 0
    return 1 if pow(value, (prime - 1) // 2, prime) == 1 else -1


def half_interval_values(prime: int) -> np.ndarray:
    midpoint = (prime - 1) // 2
    values = np.zeros(prime, dtype=np.float64)
    values[1 : midpoint + 1] = 1.0
    values[midpoint + 1 :] = -1.0
    return values


def quadratic_character_values(prime: int) -> np.ndarray:
    return np.asarray(
        [quadratic_character(value, prime) for value in range(prime)],
        dtype=np.float64,
    )


def centered_sawtooth_numerator(value: int, prime: int) -> int:
    value %= prime
    return 0 if value == 0 else 2 * value - prime


def field_carry_values(prime: int, beta: int) -> tuple[np.ndarray, int]:
    values = np.zeros(prime, dtype=np.float64)
    beta_squared = beta * beta % prime
    checks = 0
    for value in range(1, prime):
        orbit = (
            value,
            beta * value % prime,
            beta_squared * value % prime,
        )
        total = sum(orbit)
        if total == prime:
            sign = -1
        elif total == 2 * prime:
            sign = 1
        else:
            raise AssertionError("field GLV orbit did not sum to p or 2p")
        numerator = sum(
            centered_sawtooth_numerator(member, prime) for member in orbit
        )
        if numerator != sign * prime:
            raise AssertionError("field carry sawtooth identity failed")
        values[value] = float(sign)
        checks += 1
    return values, checks


def metric_by_name(case: dict[str, Any], name: str) -> dict[str, Any]:
    for metric in case["metrics"]:
        if metric["name"] == name:
            return metric
    raise KeyError(f"missing frozen spectral candidate {name!r}")


@dataclass(frozen=True)
class CandidateMetric:
    name: str
    group_max_coefficient: float
    group_max_frequency: int
    group_fourier_l1: float
    coefficient_times_sqrt_order: float
    coefficient_times_log_order: float
    coefficient_ge_inverse_log: bool
    conditional_transfer_class: str
    conditional_asymptotic_bound: str


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    beta: int
    field_carry_identity_checks: int
    half_interval_mean_abs: float
    half_interval_fourier_l1: float
    half_interval_harmonic_bound: float
    quadratic_character_mean_abs: float
    quadratic_character_nonzero_gauss_max_error: float
    quadratic_character_fourier_l1: float
    quadratic_character_exact_l1: float
    field_carry_mean_abs: float
    field_carry_fourier_l1: float
    field_carry_harmonic_bound: float
    carry_half_tensor_fourier_l1: float
    carry_half_tensor_factorization_error: float
    carry_chi_tensor_fourier_l1: float
    carry_chi_tensor_factorization_error: float
    selected_metrics: list[CandidateMetric]


def run_case(case: dict[str, Any]) -> CaseResult:
    prime = int(case["p"])
    order = int(case["order"])
    beta = int(case["beta"])
    if prime % 2 == 0 or beta in (0, 1) or pow(beta, 3, prime) != 1:
        raise AssertionError("invalid frozen odd-prime GLV case")

    half_values = half_interval_values(prime)
    chi_values = quadratic_character_values(prime)
    carry_values, carry_checks = field_carry_values(prime, beta)

    half_transform = normalized_fourier(half_values)
    chi_transform = normalized_fourier(chi_values)
    carry_transform = normalized_fourier(carry_values)

    half_l1 = float(np.sum(np.abs(half_transform)))
    chi_l1 = float(np.sum(np.abs(chi_transform)))
    carry_l1 = float(np.sum(np.abs(carry_transform)))
    harmonic_value = harmonic((prime - 1) // 2)
    half_bound = harmonic_value + 1.0
    carry_bound = 3.0 * harmonic_value
    chi_exact_l1 = (prime - 1) / math.sqrt(prime)

    if half_l1 > half_bound + 1e-9:
        raise AssertionError("half-interval Fourier-L1 bound failed")
    if carry_l1 > carry_bound + 1e-9:
        raise AssertionError("field-carry Fourier-L1 bound failed")

    expected_gauss = 1.0 / math.sqrt(prime)
    gauss_error = max(
        abs(abs(chi_transform[frequency]) - expected_gauss)
        for frequency in range(1, prime)
    )
    if gauss_error > 1e-10:
        raise AssertionError("quadratic-character Gauss spectrum failed")
    if abs(chi_l1 - chi_exact_l1) > 1e-9:
        raise AssertionError("quadratic-character Fourier-L1 identity failed")

    carry_half_tensor = np.outer(carry_transform, half_transform)
    carry_chi_tensor = np.outer(carry_transform, chi_transform)
    carry_half_l1 = float(np.sum(np.abs(carry_half_tensor)))
    carry_chi_l1 = float(np.sum(np.abs(carry_chi_tensor)))
    carry_half_factor_error = abs(carry_half_l1 - carry_l1 * half_l1)
    carry_chi_factor_error = abs(carry_chi_l1 - carry_l1 * chi_l1)
    if carry_half_factor_error > 1e-8:
        raise AssertionError("carry-half tensor L1 factorization failed")
    if carry_chi_factor_error > 1e-8:
        raise AssertionError("carry-chi tensor L1 factorization failed")

    transfer = {
        "half_y": (
            "additive Artin-Schreier plus group-character hybrid sum",
            "O(log(p)/sqrt(p))",
        ),
        "chi_y": (
            "Kummer plus group-character hybrid sum",
            "O(1/sqrt(p))",
        ),
        "field_carry_x*half_y": (
            "two-coordinate additive hybrid sum",
            "O(log(p)^2/sqrt(p))",
        ),
        "field_carry_x*chi_y": (
            "additive-Kummer plus group-character hybrid sum",
            "O(log(p)/sqrt(p))",
        ),
    }
    metrics: list[CandidateMetric] = []
    threshold = 1.0 / math.log(order)
    for name in SELECTED_CANDIDATES:
        metric = metric_by_name(case, name)
        bound_class, asymptotic = transfer[name]
        maximum = float(metric["max_nonzero_abs"])
        metrics.append(
            CandidateMetric(
                name=name,
                group_max_coefficient=maximum,
                group_max_frequency=int(metric["max_frequency"]),
                group_fourier_l1=float(metric["fourier_l1"]),
                coefficient_times_sqrt_order=maximum * math.sqrt(order),
                coefficient_times_log_order=maximum * math.log(order),
                coefficient_ge_inverse_log=maximum >= threshold,
                conditional_transfer_class=bound_class,
                conditional_asymptotic_bound=asymptotic,
            )
        )

    return CaseResult(
        p=prime,
        order=order,
        beta=beta,
        field_carry_identity_checks=carry_checks,
        half_interval_mean_abs=abs(float(half_transform[0])),
        half_interval_fourier_l1=half_l1,
        half_interval_harmonic_bound=half_bound,
        quadratic_character_mean_abs=abs(float(chi_transform[0])),
        quadratic_character_nonzero_gauss_max_error=gauss_error,
        quadratic_character_fourier_l1=chi_l1,
        quadratic_character_exact_l1=chi_exact_l1,
        field_carry_mean_abs=abs(float(carry_transform[0])),
        field_carry_fourier_l1=carry_l1,
        field_carry_harmonic_bound=carry_bound,
        carry_half_tensor_fourier_l1=carry_half_l1,
        carry_half_tensor_factorization_error=carry_half_factor_error,
        carry_chi_tensor_fourier_l1=carry_chi_l1,
        carry_chi_tensor_factorization_error=carry_chi_factor_error,
        selected_metrics=metrics,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spectral-results", type=Path, required=True)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("mixed_y_hybrid_transfer_results.json"),
    )
    args = parser.parse_args()

    spectral_data = json.loads(args.spectral_results.read_text())
    cases = [run_case(case) for case in spectral_data["cases"]]
    large_cases = [case for case in cases if case.order >= LARGE_ORDER_FLOOR]

    by_name: dict[str, list[CandidateMetric]] = {
        name: [] for name in SELECTED_CANDIDATES
    }
    for case in large_cases:
        for metric in case.selected_metrics:
            by_name[metric.name].append(metric)

    selected_large_summary = {
        name: {
            "large_cases": len(metrics),
            "cases_ge_inverse_log": sum(
                metric.coefficient_ge_inverse_log for metric in metrics
            ),
            "maximum_coefficient_times_sqrt_order": max(
                metric.coefficient_times_sqrt_order for metric in metrics
            ),
            "minimum_coefficient_times_sqrt_order": min(
                metric.coefficient_times_sqrt_order for metric in metrics
            ),
            "largest_order_coefficient": next(
                metric.group_max_coefficient
                for metric in large_cases[-1].selected_metrics
                if metric.name == name
            ),
        }
        for name, metrics in by_name.items()
    }

    payload = {
        "scope": (
            "fifteen frozen j=0 toy curves only; no external curve, point, key, "
            "wallet, or production-sized target"
        ),
        "package": "MIXED-Y-HYBRID-TRANSFER-016",
        "conditional_analytic_input": {
            "additive": (
                "For nonzero (a,b) and nontrivial scalar/group character eta, "
                "sum_P eta(P)*psi(a*x(P)+b*y(P)) is O(sqrt(p))."
            ),
            "kummer": (
                "For the quadratic field character kappa and nontrivial eta, "
                "sum_P eta(P)*kappa(y(P)) is O(sqrt(p))."
            ),
            "additive_kummer": (
                "For nonzero a and nontrivial eta, "
                "sum_P eta(P)*kappa(y(P))*psi(a*x(P)) is O(sqrt(p))."
            ),
            "status": (
                "standard fixed-conductor Weil-Deligne or character-sheaf input; "
                "source-pinned conceptually but not formalized in Lean here"
            ),
        },
        "transfer_consequences": {
            "half_y": "O(log(p)/sqrt(p))",
            "chi_y": "O(1/sqrt(p))",
            "field_carry_x*half_y": "O(log(p)^2/sqrt(p))",
            "field_carry_x*chi_y": "O(log(p)/sqrt(p))",
        },
        "cases": [asdict(case) for case in cases],
        "selected_large_summary": selected_large_summary,
        "aggregate": {
            "cases": len(cases),
            "large_cases": len(large_cases),
            "field_carry_identity_checks": sum(
                case.field_carry_identity_checks for case in cases
            ),
            "maximum_quadratic_gauss_error": max(
                case.quadratic_character_nonzero_gauss_max_error for case in cases
            ),
            "maximum_carry_half_tensor_factorization_error": max(
                case.carry_half_tensor_factorization_error for case in cases
            ),
            "maximum_carry_chi_tensor_factorization_error": max(
                case.carry_chi_tensor_factorization_error for case in cases
            ),
            "selected_large_cases_ge_inverse_log": sum(
                metric.coefficient_ge_inverse_log
                for case in large_cases
                for metric in case.selected_metrics
            ),
            "all_selected_large_candidates_below_inverse_log": all(
                not metric.coefficient_ge_inverse_log
                for case in large_cases
                for metric in case.selected_metrics
            ),
        },
        "decision": (
            "The strongest remaining half-y and carry-x times half-y observables "
            "are consistent with square-root scalar spectrum. Under the stated "
            "fixed-conductor hybrid-sum theorem, all four selected mixed-y routes "
            "are too small for a polylogarithmic local-SFT reduction."
        ),
        "remaining_open": [
            "field-permutation orientation and products containing it",
            "high-field-Fourier-L1 or high-conductor point circuits",
            "a direct public cyclotomic carry or R3 decoder",
            "formalization of the external character-sheaf square-root theorem",
        ],
        "claim_boundary": [
            "The finite Fourier and tensor identities are replayed directly.",
            "The scalar-domain spectra are bounded toy evidence, not an asymptotic theorem.",
            "The mixed additive, Kummer, and additive-Kummer O(sqrt(p)) bounds are external analytic inputs.",
            "No universal lower bound for arbitrary public predicates or ECDLP algorithms is claimed.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
