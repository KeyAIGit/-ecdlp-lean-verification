#!/usr/bin/env python3
"""Toy replay for DUAL-CHARACTER-LINEAR-SUPPORT-012.

For nonzero frequency j, let

    a=[j]_n, b=[lambda*j]_n, c=[lambda^2*j]_n.

Their sum is n or 2n. The normalized GLV-carry Fourier coefficient is

    ghat(j)=(i/n)*(cot(pi*a/n)+cot(pi*b/n)+cot(pi*c/n)).

If a+b+c=n, the cotangents x,y,z satisfy xy+yz+zx=1, hence
|x+y+z|>=sqrt(3), with positive sign. The complementary-angle case has the
opposite sign and the same bound. Therefore every nonzero frequency occurs.

The numerical replay validates conventions on the frozen toy groups. The full
support statement is analytic, not inferred from finite testing.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import mpmath as mp

from nonlocal_odd_anchor_screen import FROZEN_CASES, orbit, primitive_cube_root


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    generator: tuple[int, int]
    lam: int
    frequencies_checked: int
    nonzero_support_size: int
    expected_nonzero_support_size: int
    sign_failures: int
    sqrt_three_bound_failures: int
    minimum_unnormalized_magnitude: str
    minimum_frequency: int
    maximum_unnormalized_magnitude: str


def run_case(p: int, order: int, generator: tuple[int, int]) -> CaseResult:
    points = orbit(generator, order, p)
    beta = primitive_cube_root(p)
    lookup = {point: scalar for scalar, point in enumerate(points)}
    lam = lookup[(beta * generator[0] % p, generator[1])]
    lam2 = lam * lam % order

    mp.mp.dps = 100
    lower = mp.sqrt(3)
    support = 0
    sign_failures = 0
    bound_failures = 0
    minimum = mp.inf
    minimum_frequency = 0
    maximum = mp.mpf(0)

    for frequency in range(1, order):
        residues = (
            frequency,
            lam * frequency % order,
            lam2 * frequency % order,
        )
        total = sum(residues)
        if total not in (order, 2 * order):
            raise AssertionError("GLV residue sum is not n or 2n")
        gamma = total // order
        cot_sum = sum(
            mp.cot(mp.pi * residue / order) for residue in residues
        )
        if cot_sum:
            support += 1
        expected_sign = 1 if gamma == 1 else -1
        observed_sign = 1 if cot_sum > 0 else -1
        sign_failures += observed_sign != expected_sign
        bound_failures += abs(cot_sum) + mp.mpf("1e-80") < lower
        if abs(cot_sum) < minimum:
            minimum = abs(cot_sum)
            minimum_frequency = frequency
        maximum = max(maximum, abs(cot_sum))

    return CaseResult(
        p=p,
        order=order,
        generator=generator,
        lam=lam,
        frequencies_checked=order - 1,
        nonzero_support_size=support,
        expected_nonzero_support_size=order - 1,
        sign_failures=sign_failures,
        sqrt_three_bound_failures=bound_failures,
        minimum_unnormalized_magnitude=mp.nstr(minimum, 30),
        minimum_frequency=minimum_frequency,
        maximum_unnormalized_magnitude=mp.nstr(maximum, 30),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "dual_character_linear_support_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    payload = {
        "package": "DUAL-CHARACTER-LINEAR-SUPPORT-012",
        "scope": (
            "exact analytic support theorem and fifteen frozen toy convention "
            "replays; no external or production target"
        ),
        "fourier_formula": (
            "ghat(j)=(i/n)*(cot(pi*[j]_n/n)+cot(pi*[lambda*j]_n/n)"
            "+cot(pi*[lambda^2*j]_n/n))"
        ),
        "proof": [
            "for j!=0 the three canonical residues are nonzero and sum to n or 2n",
            "when the angles sum to pi, xy+yz+zx=1 for their cotangents",
            "therefore (x+y+z)^2>=3 and the sum is positive",
            "complementary angles handle the 2pi case and negate the sum",
            "hence every nonzero normalized Fourier coefficient has magnitude at least sqrt(3)/n",
        ],
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases": len(cases),
            "frequencies_checked": sum(
                case.frequencies_checked for case in cases
            ),
            "all_supports_full": all(
                case.nonzero_support_size
                == case.expected_nonzero_support_size
                for case in cases
            ),
            "sign_failures": sum(case.sign_failures for case in cases),
            "sqrt_three_bound_failures": sum(
                case.sqrt_three_bound_failures for case in cases
            ),
            "smallest_observed_unnormalized_magnitude": min(
                case.minimum_unnormalized_magnitude for case in cases
            ),
            "largest_order": max(case.order for case in cases),
        },
        "consequence": (
            "By uniqueness of the additive Fourier expansion, an exact linear "
            "combination of distinct additive characters representing the carry "
            "must include all n-1 nonzero frequencies. The direct sparse linear "
            "dual-character model therefore has exponential support."
        ),
        "public_carry_decoder_found": False,
        "public_R3_decoder_found": False,
        "unconditional_sub_sqrt_algorithm_found": False,
        "claim_boundary": [
            "The theorem concerns exact linear character expansions only.",
            "It does not rule out nonlinear circuits or an oracle that directly evaluates one hidden primitive character.",
            "The numerical replay validates conventions but is not the proof of full support.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
