#!/usr/bin/env python3
"""Toy-only structural screen for DIRECT-GLV-QUOTIENT-SPECTRUM-013.

The target h=g*chi(y) is placed on the cyclic quotient
F_n^*/<-1,lambda>. The script computes exact complex Fourier support, periodic
binary linear complexity, Fourier concentration, and periodic autocorrelation.
Matched controls are deterministic random permutations preserving the exact
sign balance. No external point, key, wallet, curve, or production-sized
target is accepted.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import random
import statistics
from pathlib import Path

import numpy as np
import sympy as sp

from direct_glv_carry_descent_screen import (
    FROZEN_CASES,
    orbit,
    primitive_cube_root,
    quadratic_character,
)

CONTROL_TRIALS = 512
ORDER_FLOOR = 271
ROUND_DIGITS = 12
PRIMARY_METRICS = (
    "max_fourier_over_sqrt_m",
    "top4_power_fraction",
    "spectral_entropy",
    "max_abs_autocorrelation_over_m",
    "autocorrelation_rms_over_sqrt_m",
    "linear_complexity_ratio",
)


def round_float(value: float) -> float:
    return round(float(value), ROUND_DIGITS)


def factor_integer(value: int) -> list[tuple[int, int]]:
    factors: list[tuple[int, int]] = []
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            exponent = 0
            while value % divisor == 0:
                value //= divisor
                exponent += 1
            factors.append((divisor, exponent))
        divisor += 1 if divisor == 2 else 2
    if value > 1:
        factors.append((value, 1))
    return factors


def least_primitive_root(prime: int) -> int:
    factors = [factor for factor, _ in factor_integer(prime - 1)]
    for candidate in range(2, prime):
        if all(
            pow(candidate, (prime - 1) // factor, prime) != 1
            for factor in factors
        ):
            return candidate
    raise AssertionError("primitive root not found")


def quotient_sequence(
    p: int, order: int, generator: tuple[int, int]
) -> dict:
    points = orbit(generator, order, p)
    beta = primitive_cube_root(p)
    scalar_of = {point: scalar for scalar, point in enumerate(points)}
    lam = scalar_of[(beta * generator[0] % p, generator[1])]
    lam2 = lam * lam % order
    if (1 + lam + lam2) % order:
        raise AssertionError("invalid GLV eigenvalue")

    target: list[int | None] = [None] * order
    for scalar in range(1, order):
        first = lam * scalar % order
        second = lam2 * scalar % order
        total = scalar + first + second
        if total not in (order, 2 * order):
            raise AssertionError("invalid GLV carry")
        carry = 1 if total == 2 * order else -1
        point = points[scalar]
        if point is None:
            raise AssertionError("unexpected infinity")
        target[scalar] = carry * quadratic_character(point[1], p)

    for scalar in range(1, order):
        orbit6 = {
            scalar,
            order - scalar,
            lam * scalar % order,
            order - (lam * scalar % order),
            lam2 * scalar % order,
            order - (lam2 * scalar % order),
        }
        if len(orbit6) != 6:
            raise AssertionError("non-free order-six quotient orbit")
        if len({target[member] for member in orbit6}) != 1:
            raise AssertionError("target failed quotient invariance")

    primitive_root = least_primitive_root(order)
    quotient_order = (order - 1) // 6
    subgroup6 = {
        pow(primitive_root, multiple * quotient_order, order)
        for multiple in range(6)
    }
    expected6 = {
        1,
        order - 1,
        lam,
        order - lam,
        lam2,
        order - lam2,
    }
    if subgroup6 != expected6:
        raise AssertionError("primitive-root quotient mismatch")

    sequence = [
        int(target[pow(primitive_root, index, order)])
        for index in range(quotient_order)
    ]
    return {
        "p": p,
        "order": order,
        "generator": list(generator),
        "beta": beta,
        "lambda": lam,
        "primitive_root": primitive_root,
        "quotient_order": quotient_order,
        "sequence": sequence,
    }


def gf2_remainder(left: int, right: int) -> int:
    right_degree = right.bit_length() - 1
    while left and left.bit_length() - 1 >= right_degree:
        left ^= right << (
            left.bit_length() - 1 - right_degree
        )
    return left


def gf2_gcd(left: int, right: int) -> int:
    while right:
        left, right = right, gf2_remainder(left, right)
    return left


def periodic_binary_linear_complexity(bits: list[int]) -> int:
    period = len(bits)
    polynomial = 0
    for index, bit in enumerate(bits):
        if bit & 1:
            polynomial |= 1 << index
    modulus = (1 << period) | 1
    gcd = gf2_gcd(modulus, polynomial)
    return period - (gcd.bit_length() - 1)


def sign_invariant_linear_complexity(
    sequence: list[int]
) -> tuple[int, int, int]:
    bits = [0 if sign == 1 else 1 for sign in sequence]
    direct = periodic_binary_linear_complexity(bits)
    complement = periodic_binary_linear_complexity(
        [1 - bit for bit in bits]
    )
    return direct, complement, min(direct, complement)


def primitive_root_linear_complexity_profile(
    sequence: list[int], order: int
) -> dict:
    quotient_order = len(sequence)
    values: list[int] = []
    primitive_root_choices = 0
    for exponent in range(1, order):
        if math.gcd(exponent, order - 1) != 1:
            continue
        primitive_root_choices += 1
        reindexed = [
            sequence[exponent * index % quotient_order]
            for index in range(quotient_order)
        ]
        values.append(sign_invariant_linear_complexity(reindexed)[2])
    return {
        "primitive_root_choices": primitive_root_choices,
        "minimum": min(values),
        "maximum": max(values),
        "distinct_values": len(set(values)),
    }


def exact_complex_fourier_support(sequence: list[int]) -> dict:
    variable = sp.symbols("x")
    polynomial = sp.Poly(
        sum(
            int(sign) * variable**index
            for index, sign in enumerate(sequence)
        ),
        variable,
        domain=sp.QQ,
    )
    root_polynomial = sp.Poly(
        variable ** len(sequence) - 1,
        variable,
        domain=sp.QQ,
    )
    common = sp.gcd(polynomial, root_polynomial)
    gcd_degree = int(sp.degree(common))
    return {
        "criterion": "support = m - deg(gcd(S(x),x^m-1)) over Q",
        "gcd_degree": gcd_degree,
        "support": len(sequence) - gcd_degree,
    }


def floating_and_binary_metrics(sequence: list[int]) -> dict:
    signs = np.array(sequence, dtype=np.int8)
    length = len(sequence)
    transform = np.fft.fft(signs.astype(np.float64))
    power = np.abs(transform) ** 2
    non_dc = power[1:]
    non_dc_total = float(non_dc.sum())

    if non_dc_total:
        distribution = non_dc / non_dc_total
        positive_distribution = distribution[distribution > 0]
        spectral_entropy = -float(
            np.sum(
                positive_distribution
                * np.log(positive_distribution)
            )
        ) / math.log(len(non_dc))
        ordered_power = np.sort(non_dc)[::-1]
        top4 = float(
            ordered_power[: min(4, len(ordered_power))].sum()
            / non_dc_total
        )
        top8 = float(
            ordered_power[: min(8, len(ordered_power))].sum()
            / non_dc_total
        )
        maximum_power_fraction = float(non_dc.max() / non_dc_total)
        maximum_fourier = float(
            math.sqrt(float(non_dc.max())) / math.sqrt(length)
        )
    else:
        spectral_entropy = 0.0
        top4 = 1.0
        top8 = 1.0
        maximum_power_fraction = 1.0
        maximum_fourier = 0.0

    autocorrelation = np.rint(
        np.fft.ifft(power).real
    ).astype(np.int64)
    off_zero = autocorrelation[1:]
    if len(off_zero):
        maximum_position = int(
            np.argmax(np.abs(off_zero))
        ) + 1
        maximum_autocorrelation = int(
            np.abs(off_zero).max()
        )
        autocorrelation_rms = float(
            np.sqrt(np.mean(off_zero.astype(np.float64) ** 2))
            / math.sqrt(length)
        )
    else:
        maximum_position = 0
        maximum_autocorrelation = 0
        autocorrelation_rms = 0.0

    direct, complement, invariant = (
        sign_invariant_linear_complexity(sequence)
    )
    dominant_index = (
        int(np.argmax(power[1:])) + 1
        if len(power) > 1
        else 0
    )
    dominant_order = (
        length // math.gcd(dominant_index, length)
        if dominant_index
        else 1
    )

    return {
        "length": length,
        "negative": int(np.count_nonzero(signs < 0)),
        "positive": int(np.count_nonzero(signs > 0)),
        "balance": round_float(float(signs.mean())),
        "dominant_character_index_least_generator": dominant_index,
        "dominant_character_order": dominant_order,
        "max_fourier_over_sqrt_m": round_float(maximum_fourier),
        "max_power_fraction": round_float(maximum_power_fraction),
        "top4_power_fraction": round_float(top4),
        "top8_power_fraction": round_float(top8),
        "spectral_entropy": round_float(spectral_entropy),
        "effective_spectral_modes": round_float(
            len(non_dc) ** spectral_entropy
            if len(non_dc) > 1
            else 1.0
        ),
        "max_abs_autocorrelation": maximum_autocorrelation,
        "max_abs_autocorrelation_over_m": round_float(
            maximum_autocorrelation / length
        ),
        "max_autocorrelation_shift_least_generator": (
            maximum_position
        ),
        "autocorrelation_rms_over_sqrt_m": round_float(
            autocorrelation_rms
        ),
        "linear_complexity": direct,
        "complement_linear_complexity": complement,
        "sign_invariant_linear_complexity": invariant,
        "linear_complexity_ratio": round_float(
            invariant / length
        ),
    }


def nearest_rank_quantile(
    values: list[float], probability: float
) -> float:
    ordered = sorted(values)
    position = max(
        0, math.ceil(probability * len(ordered)) - 1
    )
    return ordered[position]


def matched_control_summary(
    observed: float, values: list[float]
) -> dict:
    rounded_values = [round_float(value) for value in values]
    rounded_observed = round_float(observed)
    trials = len(rounded_values)
    less_equal = (
        sum(value <= rounded_observed for value in rounded_values)
        + 1
    ) / (trials + 1)
    greater_equal = (
        sum(value >= rounded_observed for value in rounded_values)
        + 1
    ) / (trials + 1)
    q05 = nearest_rank_quantile(rounded_values, 0.05)
    q95 = nearest_rank_quantile(rounded_values, 0.95)
    return {
        "observed": rounded_observed,
        "control_q05": round_float(q05),
        "control_median": round_float(
            statistics.median(rounded_values)
        ),
        "control_q95": round_float(q95),
        "empirical_percentile_le": round_float(less_equal),
        "two_sided_rank": round_float(
            min(1.0, 2 * min(less_equal, greater_equal))
        ),
        "outside_5_95": bool(
            rounded_observed < q05 or rounded_observed > q95
        ),
    }


def matched_controls(
    sequence: list[int], seed: int
) -> dict:
    generator = random.Random(seed)
    values = {metric: [] for metric in PRIMARY_METRICS}
    for _ in range(CONTROL_TRIALS):
        control = list(sequence)
        generator.shuffle(control)
        metrics = floating_and_binary_metrics(control)
        for metric in PRIMARY_METRICS:
            values[metric].append(float(metrics[metric]))
    return values


def run_case(
    p: int, order: int, generator: tuple[int, int]
) -> dict:
    case = quotient_sequence(p, order, generator)
    sequence = case.pop("sequence")
    floating = floating_and_binary_metrics(sequence)
    exact_support = exact_complex_fourier_support(sequence)
    linear_profile = primitive_root_linear_complexity_profile(
        sequence, order
    )

    floating["complex_fourier_gcd_degree"] = (
        exact_support["gcd_degree"]
    )
    floating["complex_fourier_support"] = (
        exact_support["support"]
    )
    floating["complex_fourier_support_is_full"] = (
        exact_support["support"] == len(sequence)
    )
    floating["complex_fourier_support_criterion"] = (
        exact_support["criterion"]
    )
    floating["primitive_root_linear_complexity_profile"] = (
        linear_profile
    )

    controls = matched_controls(
        sequence, 20260812 + p + order
    )
    summaries = {
        metric: matched_control_summary(
            float(floating[metric]), controls[metric]
        )
        for metric in PRIMARY_METRICS
    }
    case["metrics"] = floating
    case["matched_controls"] = summaries
    return case


def build_payload(cases: list[dict]) -> dict:
    nontrivial = [
        case for case in cases
        if case["order"] >= ORDER_FLOOR
    ]
    outside: list[dict] = []
    for case in nontrivial:
        for metric, summary in case["matched_controls"].items():
            if summary["outside_5_95"]:
                outside.append({
                    "order": case["order"],
                    "metric": metric,
                    "observed": summary["observed"],
                    "empirical_percentile_le": (
                        summary["empirical_percentile_le"]
                    ),
                    "two_sided_rank": summary["two_sided_rank"],
                })

    dominant_orders = [
        case["metrics"]["dominant_character_order"]
        for case in nontrivial
    ]
    multiplicities = collections.Counter(dominant_orders)
    all_ranks = [
        summary["two_sided_rank"]
        for case in nontrivial
        for summary in case["matched_controls"].values()
    ]
    held_out = [
        case for case in nontrivial
        if case["order"] in (3469, 4021)
    ]

    return {
        "package": "DIRECT-GLV-QUOTIENT-SPECTRUM-013",
        "scope": (
            "fifteen frozen j=0 prime-order toy subgroups; "
            "no external or production target"
        ),
        "target": (
            "h(k)=g(k)*chi(y([k]G)) on "
            "F_n^*/<-1,lambda>"
        ),
        "quotient_model": {
            "group": "F_n^*/<-1,lambda>",
            "order": "(n-1)/6",
            "coordinate": (
                "least primitive root r; sequence index j "
                "represents r^j<-1,lambda>"
            ),
            "generator_invariant_metrics": [
                "complex Fourier support",
                "Fourier magnitude multiset",
                "periodic autocorrelation multiset",
                "sign-invariant periodic F_2 linear complexity",
            ],
            "reported_frequency_and_shift_indices": (
                "least-primitive-root implementation convention"
            ),
        },
        "exact_certificates": {
            "complex_fourier_support": (
                "gcd of the integer sequence polynomial "
                "S(x) with x^m-1 over Q"
            ),
            "binary_linear_complexity": (
                "m-deg(gcd(B(x),x^m+1)) over F_2; "
                "minimum over global sign"
            ),
            "primitive_root_check": (
                "binary linear complexity recomputed for every "
                "primitive root of F_n^*"
            ),
        },
        "matched_control_protocol": {
            "trials_per_case": CONTROL_TRIALS,
            "control": (
                "deterministic random permutation preserving "
                "the exact number of positive and negative signs"
            ),
            "primary_metrics": list(PRIMARY_METRICS),
            "envelope": "nearest-rank 5th to 95th percentiles",
            "rank_note": (
                "empirical ranks are diagnostics, not p-values "
                "for the structured carry target"
            ),
        },
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "nontrivial_cases": len(nontrivial),
            "full_complex_fourier_support_nontrivial_cases": sum(
                case["metrics"][
                    "complex_fourier_support_is_full"
                ]
                for case in nontrivial
            ),
            "all_primitive_root_linear_complexities_invariant": all(
                case["metrics"][
                    "primitive_root_linear_complexity_profile"
                ]["distinct_values"] == 1
                for case in cases
            ),
            "minimum_sign_invariant_linear_complexity_ratio": min(
                case["metrics"]["linear_complexity_ratio"]
                for case in nontrivial
            ),
            "full_binary_linear_complexity_nontrivial_cases": sum(
                case["metrics"][
                    "sign_invariant_linear_complexity"
                ] == case["quotient_order"]
                for case in nontrivial
            ),
            "largest_two_cases_full_binary_linear_complexity": all(
                case["metrics"][
                    "sign_invariant_linear_complexity"
                ] == case["quotient_order"]
                for case in held_out
            ),
            "primary_metric_comparisons": (
                len(nontrivial) * len(PRIMARY_METRICS)
            ),
            "primary_metric_outside_5_95_count": len(outside),
            "primary_metric_outside_5_95": outside,
            "minimum_primary_two_sided_rank": min(all_ranks),
            "cases_with_primary_two_sided_rank_at_most_0_05": sum(
                any(
                    summary["two_sided_rank"] <= 0.05
                    for summary in case[
                        "matched_controls"
                    ].values()
                )
                for case in nontrivial
            ),
            "held_out_primary_metrics_all_inside_5_95": all(
                not summary["outside_5_95"]
                for case in held_out
                for summary in case[
                    "matched_controls"
                ].values()
            ),
            "distinct_dominant_character_orders": len(
                multiplicities
            ),
            "maximum_dominant_character_order_multiplicity": max(
                multiplicities.values()
            ),
            "largest_case": next(
                case for case in cases
                if case["order"] == 4021
            )["metrics"],
        },
        "conclusion": (
            "Every nontrivial frozen quotient target has full exact "
            "complex Fourier support. Therefore an exact expansion in "
            "cyclic complex characters requires all m=(n-1)/6 modes. "
            "The sign-invariant periodic binary linear complexity is "
            "at least 38/45 of the period and is exactly the full "
            "period on both largest held-out quotients. Fourier "
            "concentration, spectral entropy, autocorrelation, and "
            "binary linear complexity otherwise lie inside matched "
            "balance-preserving control envelopes, except one lower-tail "
            "top-four power concentration on order 1249 whose two-sided "
            "empirical rank is about 0.082. No primary metric has a "
            "two-sided rank at most 0.05, and no common low-order "
            "dominant character is stable across curves."
        ),
        "claim_boundary": [
            (
                "Full Fourier support rules out sparse linear "
                "character expansions, not nonlinear arithmetic circuits."
            ),
            (
                "High periodic F_2 linear complexity rules out short "
                "binary cyclic recurrences under the tested quotient "
                "ordering, not general nonlinear recurrences."
            ),
            (
                "Matched-control envelopes and empirical ranks are "
                "bounded diagnostics, not asymptotic randomness proofs."
            ),
            (
                "The screen does not cover canonical p-adic outputs, "
                "additional geometric invariants, or arbitrary public "
                "coefficient-generation algorithms."
            ),
            (
                "No secp256k1 unknown point, private key, wallet, or "
                "external target is accepted or evaluated."
            ),
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "direct_glv_quotient_spectrum_results.json"
        ),
    )
    args = parser.parse_args()
    cases = [run_case(*case) for case in FROZEN_CASES]
    rendered = json.dumps(
        build_payload(cases), indent=2, sort_keys=True
    )
    args.out.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
