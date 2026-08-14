#!/usr/bin/env python3
"""Frozen replay for the first variation of a three-term cyclic norm."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from uorc056_sparse_two_translation_resultant import (
    FROZEN_CASES,
    trinomial_determinant,
)


def derivative_weights(n: int, p: int) -> list[int]:
    nodes = list(range(n + 1))
    result: list[int] = []
    for i, x_i in enumerate(nodes):
        basis = [1]
        denominator = 1
        for j, x_j in enumerate(nodes):
            if i == j:
                continue
            updated = [0] * (len(basis) + 1)
            for degree, coefficient in enumerate(basis):
                updated[degree] = (updated[degree] - coefficient * x_j) % p
                updated[degree + 1] = (updated[degree + 1] + coefficient) % p
            basis = updated
            denominator = denominator * (x_i - x_j) % p
        result.append(basis[1] * pow(denominator, -1, p) % p)
    return result


def first_variation(p: int, n: int, k: int) -> tuple[int, int]:
    inverse_index = (n - k) % n
    coefficient = pow(2, -1, p)
    if inverse_index % 2:
        coefficient = -coefficient % p
    derivative = 2 * n * coefficient % p
    orientation = -derivative * pow(n, -1, p) % p
    return derivative, orientation


def check_case(p: int, n: int, interpolate: bool) -> dict[str, object]:
    weights = derivative_weights(n, p) if interpolate else []
    trace_checks = 0
    interpolation_checks = 0
    negation_checks = 0
    for k in range(1, n):
        derivative, orientation = first_variation(p, n, k)
        expected = p - 1 if k % 2 else 1
        if derivative != -n * expected % p or orientation != expected:
            raise AssertionError("first variation failed")
        trace_checks += 1
        if (derivative + first_variation(p, n, n - k)[0]) % p:
            raise AssertionError("negation law failed")
        negation_checks += 1
        if interpolate:
            values = [
                trinomial_determinant(p, n, k, 1, 1, t)
                for t in range(n + 1)
            ]
            recovered = sum(w * value for w, value in zip(weights, values)) % p
            if recovered != derivative:
                raise AssertionError("interpolation failed")
            interpolation_checks += 1
    return {
        "p": p,
        "n": n,
        "trace_checks": trace_checks,
        "interpolation_checks": interpolation_checks,
        "negation_checks": negation_checks,
        "passed": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    cases = [
        check_case(p, n, index < 3)
        for index, (p, n) in enumerate(FROZEN_CASES)
    ]
    payload = {
        "experiment": "UORC056_TRINOMIAL_FIRST_VARIATION_C6",
        "identity": "[t] Res(z^n-1,1+z+t*z^k)=-n*(-1)^k for 0<k<n",
        "cases": cases,
        "aggregate": {
            "trace_checks": sum(case["trace_checks"] for case in cases),
            "interpolation_checks": sum(
                case["interpolation_checks"] for case in cases
            ),
            "negation_checks": sum(case["negation_checks"] for case in cases),
            "exact_observable_verified": True,
            "compact_evaluation_found": False,
        },
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True)
    print(encoded)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(encoded + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
