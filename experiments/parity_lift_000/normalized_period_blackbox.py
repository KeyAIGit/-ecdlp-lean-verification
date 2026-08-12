#!/usr/bin/env python3
"""Exact-structure toy replay for NORMALIZED-PERIOD-BLACKBOX-032.

The replay verifies the normalized Gaussian-period/cyclotomic-unit identity,
the abstract three-factor pairing formula, calibrated GLV-carry signs, the
full-dual C3-coset permutation collapse, plus/minus-C3 covariance, distinct
dual-orbit sign signatures, and the short period recurrence.

Floating arithmetic checks conventions only. Orbit and permutation statements
are exact integer computations. No external point, private key, wallet, or
production-sized target is accepted.
"""
from __future__ import annotations

import argparse
import cmath
import json
import math
from pathlib import Path

from nonlocal_odd_anchor_screen import FROZEN_CASES, orbit, primitive_cube_root

SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
ABS_TOL = 3.0e-10
REL_TOL = 3.0e-10


def scalar_lambda(
    p: int, order: int, generator: tuple[int, int]
) -> tuple[int, int]:
    points = orbit(generator, order, p)
    beta = primitive_cube_root(p)
    point_to_scalar = {point: scalar for scalar, point in enumerate(points)}
    lam = point_to_scalar[(beta * generator[0] % p, generator[1])]
    if lam in (0, 1) or pow(lam, 3, order) != 1:
        raise AssertionError("invalid GLV eigenvalue")
    if (1 + lam + lam * lam) % order != 0:
        raise AssertionError("lambda failed its cyclotomic equation")
    return beta, lam


def carry_sign(k: int, lam: int, order: int) -> int:
    k %= order
    if k == 0:
        raise AssertionError("carry is undefined at zero")
    k1 = lam * k % order
    k2 = lam * k1 % order
    total = k + k1 + k2
    if total == order:
        return -1
    if total == 2 * order:
        return 1
    raise AssertionError("GLV representatives did not sum to n or 2n")


def c3_cosets(order: int, lam: int) -> list[tuple[int, int, int]]:
    lam2 = lam * lam % order
    visited: set[int] = set()
    result: list[tuple[int, int, int]] = []
    for a in range(1, order):
        if a in visited:
            continue
        coset = tuple(sorted({a, lam * a % order, lam2 * a % order}))
        if len(coset) != 3:
            raise AssertionError("nonzero C3 orbit had wrong size")
        visited.update(coset)
        result.append(coset)
    if len(visited) != order - 1:
        raise AssertionError("C3 cosets did not partition residues")
    return result


def pm_c3_classes(order: int, lam: int) -> list[tuple[int, ...]]:
    lam2 = lam * lam % order
    visited: set[int] = set()
    result: list[tuple[int, ...]] = []
    for a in range(1, order):
        if a in visited:
            continue
        cls = tuple(
            sorted(
                {
                    a,
                    lam * a % order,
                    lam2 * a % order,
                    (-a) % order,
                    (-lam * a) % order,
                    (-lam2 * a) % order,
                }
            )
        )
        if len(cls) != 6:
            raise AssertionError("plus/minus C3 class had wrong size")
        visited.update(cls)
        result.append(cls)
    if len(visited) != order - 1:
        raise AssertionError("plus/minus C3 classes did not partition residues")
    return result


def relative_error(left: complex, right: complex) -> float:
    return abs(left - right) / max(1.0, abs(left), abs(right))


def run_case(
    p: int, order: int, generator: tuple[int, int]
) -> dict[str, object]:
    beta, lam = scalar_lambda(p, order, generator)
    lam2 = lam * lam % order
    phases = [cmath.exp(2j * math.pi * exponent / order) for exponent in range(order)]

    def eta(exponent: int) -> complex:
        return (
            phases[exponent % order]
            + phases[(lam * exponent) % order]
            + phases[(lam2 * exponent) % order]
        )

    def resolvent(a: int, k: int) -> complex:
        value = 1.0 + 0.0j
        for multiplier in (1, lam, lam2):
            value *= 1.0 - phases[(a * multiplier * k) % order]
        return value

    def normalized(a: int, k: int) -> complex:
        denominator = resolvent(a, 1)
        if abs(denominator) <= ABS_TOL:
            raise AssertionError("normalized denominator vanished")
        return resolvent(a, k) / denominator

    c3 = c3_cosets(order, lam)
    c3_set = set(c3)
    pm_classes = pm_c3_classes(order, lam)

    identity_checks = pairing_checks = carry_checks = 0
    symmetry_checks = recurrence_checks = coset_permutation_checks = 0
    max_identity_abs = max_pairing_abs = max_recurrence_abs = 0.0
    max_reality_abs = max_symmetry_rel = 0.0
    min_resolvent = math.inf

    calibration = carry_sign(1, lam, order)
    separation_bound = 8.0 * math.sin(math.pi / order) ** 3

    for k in range(1, order):
        m = resolvent(1, k)
        anti_period = eta(k) - eta(-k)
        residual = abs(m + anti_period)
        max_identity_abs = max(max_identity_abs, residual)
        if residual > ABS_TOL:
            raise AssertionError("Gaussian-period identity drifted")
        identity_checks += 1

        u = normalized(1, k)
        max_reality_abs = max(max_reality_abs, abs(u.imag))
        if abs(u.imag) > ABS_TOL:
            raise AssertionError("normalized resolvent was not real")
        observed = 1 if u.real > 0 else -1
        expected = carry_sign(k, lam, order) * calibration
        if observed != expected:
            raise AssertionError("normalized resolvent lost carry")
        carry_checks += 1
        min_resolvent = min(min_resolvent, abs(m))

        pairing_value = 1.0 + 0.0j
        pairing_denominator = 1.0 + 0.0j
        for multiplier in (1, lam, lam2):
            pairing_value *= 1.0 - phases[(multiplier * k) % order]
            pairing_denominator *= 1.0 - phases[multiplier % order]
        pairing_value /= pairing_denominator
        pairing_residual = abs(pairing_value - u)
        max_pairing_abs = max(max_pairing_abs, pairing_residual)
        if pairing_residual > ABS_TOL:
            raise AssertionError("pairing blackbox identity drifted")
        pairing_checks += 1

    if min_resolvent + ABS_TOL < separation_bound:
        raise AssertionError("sine-product separation bound failed")

    s = eta(1)
    t = eta(-1)
    powers = [eta(m) for m in range(order + 3)]
    for m in range(order):
        predicted = s * powers[m + 2] - t * powers[m + 1] + powers[m]
        residual = abs(powers[m + 3] - predicted)
        max_recurrence_abs = max(max_recurrence_abs, residual)
        if residual > 2.0e-8:
            raise AssertionError("period recurrence drifted")
        recurrence_checks += 1

    for cls in pm_classes:
        representative = cls[0]
        sample_scalars = range(1, order) if order <= 1100 else range(1, order, 7)
        for k in sample_scalars:
            reference = normalized(representative, k)
            for a in cls[1:]:
                candidate = normalized(a, k)
                residual = relative_error(candidate, reference)
                max_symmetry_rel = max(max_symmetry_rel, residual)
                if residual > REL_TOL:
                    raise AssertionError("plus/minus C3 covariance failed")
                symmetry_checks += 1

    for k in range(1, order):
        mapped = {
            tuple(sorted({k * value % order for value in coset})) for coset in c3
        }
        if mapped != c3_set:
            raise AssertionError("scalar multiplication did not permute C3 cosets")
        coset_permutation_checks += 1

    signatures: dict[bytes, int] = {}
    for cls in pm_classes:
        a = cls[0]
        calibration_a = carry_sign(a, lam, order)
        signature = bytes(
            1 if carry_sign(a * k, lam, order) * calibration_a == 1 else 0
            for k in range(1, order)
        )
        if signature in signatures:
            raise AssertionError("distinct dual classes shared a sign signature")
        signatures[signature] = a

    return {
        "p": p,
        "order": order,
        "generator": generator,
        "beta": beta,
        "lambda": lam,
        "c3_cosets": len(c3),
        "expected_c3_cosets": (order - 1) // 3,
        "pm_c3_classes": len(pm_classes),
        "expected_pm_c3_classes": (order - 1) // 6,
        "distinct_complete_signatures": len(signatures),
        "identity_checks": identity_checks,
        "pairing_blackbox_checks": pairing_checks,
        "carry_sign_checks": carry_checks,
        "pm_c3_symmetry_checks": symmetry_checks,
        "c3_coset_permutation_checks": coset_permutation_checks,
        "recurrence_checks": recurrence_checks,
        "minimum_resolvent_magnitude": min_resolvent,
        "separation_lower_bound": separation_bound,
        "maximum_identity_absolute_residual": max_identity_abs,
        "maximum_pairing_absolute_residual": max_pairing_abs,
        "maximum_recurrence_absolute_residual": max_recurrence_abs,
        "maximum_reality_absolute_residual": max_reality_abs,
        "maximum_symmetry_relative_residual": max_symmetry_rel,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("normalized_period_blackbox_results.json"),
    )
    args = parser.parse_args()

    cases = [run_case(p, order, generator) for p, order, generator in FROZEN_CASES]
    states = (SECP256K1_N - 1) // 6
    aggregate = {
        "cases": len(cases),
        "total_identity_checks": sum(row["identity_checks"] for row in cases),
        "total_pairing_blackbox_checks": sum(
            row["pairing_blackbox_checks"] for row in cases
        ),
        "total_carry_sign_checks": sum(row["carry_sign_checks"] for row in cases),
        "total_pm_c3_symmetry_checks": sum(
            row["pm_c3_symmetry_checks"] for row in cases
        ),
        "total_c3_coset_permutation_checks": sum(
            row["c3_coset_permutation_checks"] for row in cases
        ),
        "total_recurrence_checks": sum(row["recurrence_checks"] for row in cases),
        "all_c3_counts_exact": all(
            row["c3_cosets"] == row["expected_c3_cosets"] for row in cases
        ),
        "all_pm_c3_counts_exact": all(
            row["pm_c3_classes"] == row["expected_pm_c3_classes"] for row in cases
        ),
        "all_dual_signatures_distinct": all(
            row["distinct_complete_signatures"] == row["pm_c3_classes"]
            for row in cases
        ),
        "maximum_identity_absolute_residual": max(
            row["maximum_identity_absolute_residual"] for row in cases
        ),
        "maximum_pairing_absolute_residual": max(
            row["maximum_pairing_absolute_residual"] for row in cases
        ),
        "maximum_recurrence_absolute_residual": max(
            row["maximum_recurrence_absolute_residual"] for row in cases
        ),
        "maximum_reality_absolute_residual": max(
            row["maximum_reality_absolute_residual"] for row in cases
        ),
        "maximum_symmetry_relative_residual": max(
            row["maximum_symmetry_relative_residual"] for row in cases
        ),
    }
    payload = {
        "package": "NORMALIZED-PERIOD-BLACKBOX-032",
        "scope": (
            "frozen toy C3/cyclotomic replay and abstract dual-pairing phase; "
            "no external point, key, wallet, or production-sized target"
        ),
        "cases": cases,
        "secp256k1": {
            "order": SECP256K1_N,
            "dual_c3_cosets": (SECP256K1_N - 1) // 3,
            "dual_pm_c3_orbit_choices": states,
            "gaussian_period_conjugate_pairs": states,
            "generator_oriented_half_kernel_degree": states,
        },
        "aggregate": aggregate,
        "decision": (
            "U_G has an exact three-factor pairing/cyclotomic-unit blackbox once "
            "a faithful dual phase is supplied. Full dual norm is constant and "
            "normalization at G leaves (n-1)/6 dual plus/minus-C3 choices. No "
            "public sub-square-root orbit selector is obtained."
        ),
        "claim_boundary": [
            "Floating replay validates identities and signs only on frozen toy cases.",
            "The exact full-norm collapse follows from scalar permutation of C3 cosets.",
            "Distinct toy signatures do not prove a circuit lower bound.",
            "The pairing phase is simulated abstractly; no secp256k1 extension torsion is constructed.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
