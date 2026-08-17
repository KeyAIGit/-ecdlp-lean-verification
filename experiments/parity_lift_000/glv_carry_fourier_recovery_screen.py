#!/usr/bin/env python3
"""Toy-only spectral certificate for GLV-CARRY-FOURIER-REDUCTION-007.

No external curve, point, key, wallet, or production-sized target is accepted.
The script studies only the frozen j=0 prime-order toy subgroups.

For the known carry sign g on Z/nZ and a hidden nonzero scalar k, an exact carry
oracle on [t]Q returns

    F_k(t) = g(t*k mod n).

With normalized additive Fourier transform,

    Fhat_k(j) = ghat(j*k^(-1)).

Thus the heavy Fourier spectrum is multiplicatively shifted by k. The script
certifies the known carry spectrum, its L1 bound, and recovery from the two
heavy-frequency lists. It does not implement the external local sparse-Fourier
algorithm used by the reduction theorem.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

from nonlocal_odd_anchor_screen import FROZEN_CASES, orbit, primitive_cube_root

THRESHOLD = 0.25


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    generator: tuple[int, int]
    lam: int
    lam_squared: int
    threshold: float
    heavy_frequencies: list[int]
    expected_c6_frequencies: list[int]
    heavy_set_exactly_c6: bool
    minimum_heavy_magnitude: float
    maximum_nonheavy_magnitude: float
    normalized_fourier_l1: float
    theoretical_l1_bound_3H: float
    hidden_multipliers_recovered: int
    maximum_candidate_list_size: int


def normalized_carry_fourier_magnitude(
    frequency: int, order: int, lam: int, lam_squared: int
) -> float:
    """Exact cotangent formula for every nonzero frequency."""
    if frequency % order == 0:
        return 0.0
    residues = (
        frequency % order,
        lam * frequency % order,
        lam_squared * frequency % order,
    )
    imaginary = sum(
        1 / math.tan(math.pi * residue / order)
        for residue in residues
    )
    return abs(imaginary) / order


def run_case(p: int, order: int, generator: tuple[int, int]) -> CaseResult:
    points = orbit(generator, order, p)
    beta = primitive_cube_root(p)
    lookup = {point: scalar for scalar, point in enumerate(points)}
    lam = lookup[(beta * generator[0] % p, generator[1])]
    lam_squared = lam * lam % order

    magnitudes = [0.0] * order
    for frequency in range(1, order):
        magnitudes[frequency] = normalized_carry_fourier_magnitude(
            frequency, order, lam, lam_squared
        )

    heavy = {
        frequency
        for frequency in range(1, order)
        if magnitudes[frequency] >= THRESHOLD
    }
    expected = {
        1,
        order - 1,
        lam,
        order - lam,
        lam_squared,
        order - lam_squared,
    }

    half = (order - 1) // 2
    harmonic = sum(1 / value for value in range(1, half + 1))
    l1_bound = 3 * harmonic
    actual_l1 = sum(magnitudes)
    if actual_l1 > l1_bound + 1e-8:
        raise AssertionError("normalized Fourier L1 bound failed")

    recovered = 0
    maximum_candidates = 0
    for hidden in range(1, order):
        hidden_heavy = {hidden * frequency % order for frequency in heavy}
        candidates = {
            shifted * pow(base, -1, order) % order
            for shifted in hidden_heavy
            for base in heavy
        }
        if hidden not in candidates:
            raise AssertionError("heavy-spectrum candidate list lost hidden scalar")
        recovered += 1
        maximum_candidates = max(maximum_candidates, len(candidates))

    nonheavy = [
        magnitudes[frequency]
        for frequency in range(1, order)
        if frequency not in heavy
    ]

    return CaseResult(
        p=p,
        order=order,
        generator=generator,
        lam=lam,
        lam_squared=lam_squared,
        threshold=THRESHOLD,
        heavy_frequencies=sorted(heavy),
        expected_c6_frequencies=sorted(expected),
        heavy_set_exactly_c6=heavy == expected,
        minimum_heavy_magnitude=min(magnitudes[frequency] for frequency in heavy),
        maximum_nonheavy_magnitude=max(nonheavy, default=0.0),
        normalized_fourier_l1=actual_l1,
        theoretical_l1_bound_3H=l1_bound,
        hidden_multipliers_recovered=recovered,
        maximum_candidate_list_size=maximum_candidates,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("glv_carry_fourier_recovery_results.json"),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    payload = {
        "scope": "fifteen frozen j=0 prime-order toy subgroups; no external or production target",
        "package": "GLV-CARRY-FOURIER-REDUCTION-007",
        "fourier_convention": (
            "fhat(j)=(1/n)*sum_t f(t)*exp(-2*pi*i*j*t/n)"
        ),
        "decimation_identity": "F_k(t)=g(k*t) implies Fhat_k(j)=ghat(j*k^(-1))",
        "threshold": THRESHOLD,
        "l1_bound": (
            "||ghat||_1 <= (3/n)*sum_(j=1)^(n-1)|cot(pi*j/n)| "
            "<= 3*H_((n-1)/2) = O(log n)"
        ),
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases": len(cases),
            "all_heavy_sets_exactly_c6": all(
                case.heavy_set_exactly_c6 for case in cases
            ),
            "hidden_multipliers_recovered": sum(
                case.hidden_multipliers_recovered for case in cases
            ),
            "maximum_candidate_list_size": max(
                case.maximum_candidate_list_size for case in cases
            ),
            "minimum_heavy_magnitude": min(
                case.minimum_heavy_magnitude for case in cases
            ),
            "maximum_nonheavy_magnitude": max(
                case.maximum_nonheavy_magnitude for case in cases
            ),
            "maximum_actual_normalized_l1": max(
                case.normalized_fourier_l1 for case in cases
            ),
            "largest_order": max(case.order for case in cases),
        },
        "fixed_public_secp256k1": {
            "n_hex": "0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141",
            "lambda_hex": "0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72",
            "lambda_squared_hex": "0xac9c52b33fa3cf1f5ad9e3fd77ed9ba4a880b9fc8ec739c2e0cfc810b51283ce",
            "principal_normalized_magnitude": "0.31830988618379067153776752674502872406891929148091289749533468811779359526845307",
            "one_over_pi": "0.31830988618379067153776752674502872406891929148091254479737151286906912144213049",
            "normalized_l1_upper_bound_3H_approx": "531.989240123062760286002109186",
        },
        "conclusion": (
            "An exact GLV carry oracle gives query access to a multiplicatively "
            "decimated known Boolean function with a constant-heavy additive "
            "Fourier spectrum and logarithmic normalized Fourier L1 norm. A local "
            "sparse-Fourier algorithm over Z/nZ returns heavy lists for the known "
            "function and the hidden decimation; their cross-ratios contain the "
            "secret scalar, and at most six candidates remain in every frozen case."
        ),
        "claim_boundary": [
            "The spectral and candidate-list identities are exact.",
            "The external local SFT theorem is source-pinned separately; this script does not reimplement it.",
            "The reduction assumes an exact public carry oracle on arbitrary chosen scalar multiples.",
            "No carry oracle or EDS-residue decoder is constructed here.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
