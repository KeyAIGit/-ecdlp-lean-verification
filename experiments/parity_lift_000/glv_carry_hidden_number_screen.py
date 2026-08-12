#!/usr/bin/env python3
"""Toy-only structural screen for GLV-CARRY-HIDDEN-NUMBER-006.

The program accepts no external curve, point, key, wallet, or production-sized
target. It studies only the frozen j=0 prime-order toy subgroups already used by
PARITY-LIFT-000.

For a primitive order-three scalar lambda and a nonzero canonical scalar k, put

    r = lambda*k mod n,
    gamma(k) = (k + r + lambda*r mod n) / n in {1,2}.

The exact identity

    gamma(k)=1  iff  k+r<n

makes the GLV canonical-lift carry a triangular predicate on the permutation
lattice k -> lambda*k mod n. The screen measures its correlation with the
canonical most-significant bit and its principal Fourier coefficient.
"""
from __future__ import annotations

import argparse
import cmath
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

from nonlocal_odd_anchor_screen import (
    FROZEN_CASES,
    berlekamp_massey_complexity,
    orbit,
    primitive_cube_root,
)


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    generator: tuple[int, int]
    beta: int
    lam: int
    lam_squared: int
    triangle_checks: int
    triangle_identity_passed: bool
    lambda_invariance_passed: bool
    negation_complement_passed: bool
    msb_matches: int
    msb_total: int
    msb_best_accuracy: float
    advantage_over_half: float
    principal_fourier_frequency: int
    principal_fourier_real: float
    principal_fourier_imag: float
    principal_fourier_abs: float
    principal_fourier_normalized: float
    cotangent_formula_value: float
    cotangent_formula_error: float
    normalized_minus_one_over_pi: float
    carry_linear_complexity: int


def run_case(p: int, order: int, generator: tuple[int, int]) -> CaseResult:
    points = orbit(generator, order, p)
    beta = primitive_cube_root(p)
    point_to_scalar = {point: scalar for scalar, point in enumerate(points)}
    lam = point_to_scalar[(beta * generator[0] % p, generator[1])]
    lam_squared = lam * lam % order
    if lam in (0, 1) or pow(lam, 3, order) != 1:
        raise AssertionError("GLV scalar does not have exact order three")
    if (lam_squared + lam + 1) % order:
        raise AssertionError("GLV scalar failed its Eisenstein polynomial")

    gamma = [0] * order
    carry_sign = [0] * order
    triangle_ok = True

    for scalar in range(1, order):
        first = lam * scalar % order
        second = lam_squared * scalar % order
        total = scalar + first + second
        if total not in (order, 2 * order):
            raise AssertionError("canonical GLV representatives do not sum to n or 2n")
        value = total // order
        gamma[scalar] = value
        carry_sign[scalar] = 1 if value == 2 else -1
        triangle_ok &= (value == 1) == (scalar + first < order)

    lambda_invariant = all(
        gamma[lam * scalar % order] == gamma[scalar]
        for scalar in range(1, order)
    )
    negation_complement = all(
        gamma[order - scalar] == 3 - gamma[scalar]
        for scalar in range(1, order)
    )

    # Canonical MSB sign: +1 on the upper half, -1 on the lower half.
    msb = [0] + [1 if 2 * scalar > order else -1 for scalar in range(1, order)]
    raw_matches = sum(
        carry_sign[scalar] == msb[scalar]
        for scalar in range(1, order)
    )
    best_matches = max(raw_matches, order - 1 - raw_matches)
    accuracy = best_matches / (order - 1)

    # Because the carry is lambda-invariant, Fourier coefficients are constant
    # on the frequency orbit {1,lambda,lambda^2}. We record frequency one.
    coefficient = sum(
        carry_sign[scalar]
        * cmath.exp(-2j * math.pi * scalar / order)
        for scalar in range(1, order)
    )

    # Exact finite-sum formula derived from
    # floor((lambda+1)k/n)-floor(lambda*k/n):
    #   G_hat(1) = i*(cot(pi/n)+cot(pi*lambda/n)+cot(pi*lambda^2/n)).
    cotangent_value = (
        1 / math.tan(math.pi / order)
        + 1 / math.tan(math.pi * lam / order)
        + 1 / math.tan(math.pi * lam_squared / order)
    )
    formula_error = abs(coefficient - 1j * cotangent_value)
    if formula_error > 1e-6:
        raise AssertionError("principal Fourier cotangent formula failed")

    return CaseResult(
        p=p,
        order=order,
        generator=generator,
        beta=beta,
        lam=lam,
        lam_squared=lam_squared,
        triangle_checks=order - 1,
        triangle_identity_passed=triangle_ok,
        lambda_invariance_passed=lambda_invariant,
        negation_complement_passed=negation_complement,
        msb_matches=best_matches,
        msb_total=order - 1,
        msb_best_accuracy=accuracy,
        advantage_over_half=accuracy - 0.5,
        principal_fourier_frequency=1,
        principal_fourier_real=coefficient.real,
        principal_fourier_imag=coefficient.imag,
        principal_fourier_abs=abs(coefficient),
        principal_fourier_normalized=abs(coefficient) / order,
        cotangent_formula_value=cotangent_value,
        cotangent_formula_error=formula_error,
        normalized_minus_one_over_pi=abs(coefficient) / order - 1 / math.pi,
        carry_linear_complexity=berlekamp_massey_complexity(carry_sign[1:]),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("glv_carry_hidden_number_results.json"),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    large = [case for case in cases if case.order >= 500]

    payload = {
        "scope": "fifteen frozen j=0 prime-order toy subgroups; no external or production target",
        "package": "GLV-CARRY-HIDDEN-NUMBER-006",
        "predicate": (
            "gamma(k)=1 iff k + (lambda*k mod n) < n; "
            "carry_sign=+1 for gamma=2 and -1 for gamma=1"
        ),
        "principal_fourier_formula": (
            "Ghat(1)=i*(cot(pi/n)+cot(pi*lambda/n)+cot(pi*lambda^2/n))"
        ),
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases": len(cases),
            "triangle_checks": sum(case.triangle_checks for case in cases),
            "all_triangle_identities_passed": all(
                case.triangle_identity_passed for case in cases
            ),
            "all_lambda_invariance_checks_passed": all(
                case.lambda_invariance_passed for case in cases
            ),
            "all_negation_complement_checks_passed": all(
                case.negation_complement_passed for case in cases
            ),
            "minimum_msb_accuracy": min(case.msb_best_accuracy for case in cases),
            "maximum_msb_accuracy": max(case.msb_best_accuracy for case in cases),
            "large_order_cases": len(large),
            "large_order_mean_msb_accuracy": sum(
                case.msb_best_accuracy for case in large
            ) / len(large),
            "large_order_mean_advantage": sum(
                case.advantage_over_half for case in large
            ) / len(large),
            "maximum_large_order_abs_normalized_error_from_one_over_pi": max(
                abs(case.normalized_minus_one_over_pi) for case in large
            ),
            "largest_order": max(case.order for case in cases),
        },
        "conclusion": (
            "The GLV canonical-lift carry is a rigid triangular predicate, not a "
            "pseudorandom bit. Across the frozen family it predicts the canonical "
            "most-significant bit with about 75 percent accuracy and has a Fourier "
            "coefficient of linear size, asymptotically close to n/pi in the large "
            "cases. A public carry oracle would therefore be a constant-advantage "
            "hidden-number-style leakage oracle. This package does not yet prove a "
            "reduction from that oracle to ECDLP."
        ),
        "claim_boundary": [
            "The triangle identity and Fourier finite-sum formula are exact; the 75 percent statement is bounded cross-order evidence.",
            "No polynomial-time hidden-number reduction is claimed until its oracle assumptions and success bounds are proved literally.",
            "No external point, key, wallet, or production-sized target is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
