#!/usr/bin/env python3
"""Exact-structure toy replay for NORMALIZED-PERIOD-BLACKBOX-032.

The script uses only frozen small j=0 prime-order subgroups. It verifies:

* the normalized Gaussian-period resolvent equals a C3 norm of a cyclotomic
  q-integer;
* the same value is the abstract three-factor pairing blackbox once a faithful
  dual phase is supplied;
* negation and C3 multiplication leave the normalized dual-orbit function
  unchanged;
* multiplication by a nonzero scalar permutes all dual C3 cosets, so the full
  dual norm is constant;
* the sign of the distinguished normalized value is the calibrated GLV carry;
* distinct plus/minus-C3 dual classes have distinct complete sign signatures
  on the frozen cases;
* the order-three power-sum recurrence is exact up to floating replay error.

Floating arithmetic checks implementation conventions only. Orbit counts and
permutation statements are exact integer computations. No external point,
private key, wallet, or production-sized target is accepted.
"""
from __future__ import annotations

import argparse
import cmath
import json
import math
from pathlib import Path

from nonlocal_odd_anchor_screen import FROZEN_CASES, orbit, primitive_cube_root

SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
TOLERANCE = 3.0e-10


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
        raise AssertionError("lambda failed 1+lambda+lambda^2=0")
    return beta, lam


def carry_sign(k: int, lam: int, order: int) -> int:
    k1 = lam * k % order
    k2 = lam * k1 % order
    total = k + k1 + k2
    if total == order:
        return -1
    if total == 2 * order:
        return 1
    raise AssertionError("canonical GLV representatives did not sum to n or 2n")


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
        raise AssertionError("C3 cosets did not partition nonzero residues")
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
        exponents = (
            a * k % order,
            a * lam * k % order,
            a * lam2 * k % order,
        )
        value = 1.0 + 0.0j
        for exponent in exponents:
            value *= 1.0 - phases[exponent]
        return value

    def normalized(a: int, k: int) -> complex:
        denominator = resolvent(a, 1)
        if abs(denominator) <= TOLERANCE:
            raise AssertionError("normalized resolvent denominator vanished")
        return resolvent(a, k) / denominator

    c3 = c3_cosets(order, lam)
    c3_set = set(c3)
    pm_classes = pm_c3_classes(order, lam)

    identity_checks = 0
    pairing_checks = 0
    carry_checks = 0
    symmetry_checks = 0
    recurrence_checks = 0
    coset_permutation_checks = 0
    maximum_identity_residual = 0.0
    maximum_pairing_residual = 0.0
    maximum_recurrence_residual = 0.0
    maximum_reality_residual = 0.0
    minimum_resolvent_magnitude = math.inf

    calibration = carry_sign(1, lam, order)
    lower_bound = 8.0 * math.sin(math.pi / order) ** 3

    # The distinguished dual orbit a=1.
    for k in range(1, order):
        m = resolvent(1, k)
        a = eta(k) - eta(-k)
        # M = conjugate(eta)-eta = -A; ratios agree.
        residual = abs(m + a)
        maximum_identity_residual = max(maximum_identity_residual, residual)
        if residual > TOLERANCE:
            raise AssertionError("Gaussian-period/cyclotomic-unit identity drifted")
        identity_checks += 1

        u = normalized(1, k)
        maximum_reality_residual = max(maximum_reality_residual, abs(u.imag))
        if abs(u.imag) > TOLERANCE:
            raise AssertionError("normalized resolvent was not real")
        observed = 1 if u.real > 0 else -1
        expected = carry_sign(k, lam, order) * calibration
        if observed != expected:
            raise AssertionError("normalized resolvent lost calibrated carry")
        carry_checks += 1

        minimum_resolvent_magnitude = min(minimum_resolvent_magnitude, abs(m))

        # Abstract pairing simulation: e([m]G,T)=zeta^m.
        pairing_value = 1.0 + 0.0j
        pairing_denominator = 1.0 + 0.0j
        for multiplier in (1, lam, lam2):
            pairing_value *= 1.0 - phases[(multiplier * k) % order]
            pairing_denominator *= 1.0 - phases[multiplier % order]
        pairing_value /= pairing_denominator
        pairing_residual = abs(pairing_value - u)
        maximum_pairing_residual = max(maximum_pairing_residual, pairing_residual)
        if pairing_residual > TOLERANCE:
            raise AssertionError("pairing blackbox formula drifted")
        pairing_checks += 1

    if minimum_resolvent_magnitude + TOLERANCE < lower_bound:
        raise AssertionError("sine-product separation bound failed")

    # The power sums obey a third-order recurrence over the period coefficient
    # field. This is short in recurrence order but does not remove the unknown
    # index or the faithful phase coefficients.
    s = eta(1)
    t = eta(-1)
    pows = [eta(m) for m in range(order + 3)]
    for m in range(order):
        predicted = s * pows[m + 2] - t * pows[m + 1] + pows[m]
        recurrence_residual = abs(pows[m + 3] - predicted)
        maximum_recurrence_residual = max(
            maximum_recurrence_residual, recurrence_residual
        )
        if recurrence_residual > 2.0e-8:
            raise AssertionError("order-three period recurrence drifted")
        recurrence_checks += 1

    # U_a is constant on plus/minus C3 classes.
    for cls in pm_classes:
        representative = cls[0]
        sample_scalars = range(1, order) if order <= 1100 else range(1, order, 7)
        for k in sample_scalars:
            reference = normalized(representative, k)
            for a in cls[1:]:
                residual = abs(normalized(a, k) - reference)
                maximum_identity_residual = max(maximum_identity_residual, residual)
                if residual > 2.0e-9:
                    raise AssertionError("plus/minus C3 covariance failed")
                symmetry_checks += 1

    # Multiplication by every nonzero k permutes all C3 cosets. This is the
    # exact combinatorial content of the full dual norm collapse.
    for k in range(1, order):
        mapped = {
            tuple(sorted({k * value % order for value in coset})) for coset in c3
        }
        if mapped != c3_set:
            raise AssertionError("scalar multiplication did not permute C3 cosets")
        coset_permutation_checks += 1

    # Distinct dual plus/minus-C3 classes produce distinct complete carry-ratio
    # signatures on every frozen case.
    signatures: dict[bytes, int] = {}
    for cls in pm_classes:
        a = cls[0]
        calibration_a = carry_sign(a, lam, order)
        signature = bytes(
            1 if carry_sign(a * k % order, lam, order) * calibration_a == 1 else 0
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
        "minimum_resolvent_magnitude": minimum_resolvent_magnitude,
        "separation_lower_bound": lower_bound,
        "maximum_identity_residual": maximum_identity_residual,
        "maximum_pairing_residual": maximum_pairing_residual,
        "maximum_recurrence_residual": maximum_recurrence_residual,
        "maximum_reality_residual": maximum_reality_residual,
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
    secp_states = (SECP256K1_N - 1) // 6
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
            "dual_pm_c3_orbit_choices": secp_states,
            "gaussian_period_conjugate_pairs": secp_states,
            "generator_oriented_half_kernel_degree": secp_states,
        },
        "aggregate": {
            "cases": len(cases),
            "total_identity_checks": sum(int(row["identity_checks"]) for row in cases),
            "total_pairing_blackbox_checks": sum(
                int(row["pairing_blackbox_checks"]) for row in cases
            ),
            "total_carry_sign_checks": sum(
                int(row["carry_sign_checks"]) for row in cases
            ),
            "total_pm_c3_symmetry_checks": sum(
                int(row["pm_c3_symmetry_checks"]) for row in cases
            ),
            "total_c3_coset_permutation_checks": sum(
                int(row["c3_coset_permutation_checks"]) for row in cases
            ),
            "total_recurrence_checks": sum(
                int(row["recurrence_checks"]) for row in cases
            ),
            "all_c3_counts_exact": all(
                row["c3_cosets"] == row["expected_c3_cosets"] for row in cases
            ),
            "all_pm_c3_counts_exact": all(
                row["pm_c3_classes"] == row["expected_pm_c3_classes"]
                for row in cases
            ),
            "all_dual_signatures_distinct": all(
                row["distinct_complete_signatures"] == row["pm_c3_classes"]
                for row in cases
            ),
            "maximum_identity_residual": max(
                float(row["maximum_identity_residual"]) for row in cases
            ),
            "maximum_pairing_residual": max(
                float(row["maximum_pairing_residual"]) for row in cases
            ),
            "maximum_recurrence_residual": max(
                float(row["maximum_recurrence_residual"]) for row in cases
            ),
            "maximum_reality_residual": max(
                float(row["maximum_reality_residual"]) for row in cases
            ),
        },
        "decision": (
            "U_G has an exact three-factor pairing/cyclotomic-unit blackbox once "
            "a faithful dual phase is supplied. Full dual-kernel norm is constant, "
            "and normalization at G leaves (n-1)/6 distinct dual plus/minus-C3 "
            "orbit choices. No public sub-square-root orbit selector is obtained."
        ),
        "claim_boundary": [
            "Floating replay validates identities and signs only on frozen toy cases.",
            "The exact full-norm collapse follows from scalar permutation of C3 cosets.",
            "Distinct toy signatures do not prove a circuit lower bound.",
            "The script simulates the pairing phase abstractly and does not construct n-torsion over secp256k1 extension fields.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
