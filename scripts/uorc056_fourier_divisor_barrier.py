#!/usr/bin/env python3
"""Exact parity Fourier peak and conditional divisor-support lower bounds.

This is a public-parameter, theorem-instrumentation script. It accepts no
external point, scalar, wallet or production target.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import mpmath as mp

SECP_P = 2**256 - 2**32 - 977
SECP_N = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16
)
FROZEN_ODD_ORDERS = (31, 79, 67, 127, 139)
BOUND_CONSTANTS = (1, 2, 4, 8)


def stable_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def peak_frequency(n: int) -> int:
    if n < 3 or n % 2 == 0:
        raise ValueError("n must be odd and at least three")
    return (n - 1) // 2


def direct_nonidentity_fourier(n: int, r: int) -> complex:
    omega = mp.e ** (-2j * mp.pi * r / n)
    return sum(((-1) ** k) * omega**k for k in range(1, n))


def closed_nonidentity_fourier(n: int, r: int) -> complex:
    z = mp.e ** (-2j * mp.pi * r / n)
    return (1 - z) / (1 + z)


def peak_magnitude(n: int) -> mp.mpf:
    return mp.cot(mp.pi / (2 * n))


def conditional_support_lower_bound(
    p: int, n: int, trace_constant: int
) -> int:
    """Return ceil((cot(pi/2n)-1)/(C*sqrt(p)+1)).

    The inequality is conditional on a hybrid trace estimate

        |sum eta(P) chi(R(P))| <= C*s*sqrt(p),

    where s is the geometric odd-valuation support size. The extra s+1 term
    permits regularization on all support points and omission of the identity.
    """
    numerator = peak_magnitude(n) - 1
    denominator = trace_constant * mp.sqrt(p) + 1
    return int(mp.ceil(numerator / denominator))


def run() -> dict[str, object]:
    mp.mp.dps = 140
    checks: list[dict[str, object]] = []
    for n in FROZEN_ODD_ORDERS:
        r = peak_frequency(n)
        direct = direct_nonidentity_fourier(n, r)
        closed = closed_nonidentity_fourier(n, r)
        peak = peak_magnitude(n)
        checks.append(
            {
                "n": n,
                "frequency": r,
                "direct_vs_closed_absolute_error": mp.nstr(abs(direct - closed), 12),
                "closed_magnitude_vs_cot_error": mp.nstr(abs(abs(closed) - peak), 12),
                "peak_magnitude": mp.nstr(peak, 50),
                "peak_over_n": mp.nstr(peak / n, 50),
            }
        )
        if abs(direct - closed) > mp.mpf("1e-120"):
            raise AssertionError("geometric-series Fourier identity drifted")
        if abs(abs(closed) - peak) > mp.mpf("1e-120"):
            raise AssertionError("cotangent peak identity drifted")

    secp_peak = peak_magnitude(SECP_N)
    lower_bounds = {
        f"C={constant}": conditional_support_lower_bound(
            SECP_P, SECP_N, constant
        )
        for constant in BOUND_CONSTANTS
    }
    payload: dict[str, object] = {
        "schema_version": "1.0",
        "experiment": "UORC-056-FOURIER-DIVISOR-BARRIER-V7",
        "elementary_identity": {
            "sequence": "s(k)=(-1)^k for 1<=k<n, n odd",
            "transform": "sum_{k=1}^{n-1} s(k) z^k = (1-z)/(1+z) when z^n=1 and z!=1",
            "peak_frequency": "r=(n-1)/2",
            "peak_magnitude": "cot(pi/(2n))",
            "asymptotic_ratio": "cot(pi/(2n))/n -> 2/pi",
        },
        "frozen_replays": checks,
        "secp256k1": {
            "p": str(SECP_P),
            "n": str(SECP_N),
            "cofactor": 1,
            "peak_frequency": str(peak_frequency(SECP_N)),
            "peak_magnitude": mp.nstr(secp_peak, 110),
            "peak_over_n": mp.nstr(secp_peak / SECP_N, 110),
            "peak_over_sqrt_p": mp.nstr(secp_peak / mp.sqrt(SECP_P), 110),
            "conditional_odd_divisor_support_lower_bounds": {
                key: str(value) for key, value in lower_bounds.items()
            },
        },
        "conditional_bridge": {
            "hypothesis": "For every nontrivial group character eta and quadratic Kummer trace chi(R), the complete hybrid sum is at most C*s*sqrt(p), where s is the geometric odd-valuation support of R.",
            "regularization_allowance": "Changing values on at most s divisor-support points and omitting the identity changes the Fourier coefficient by at most s+1.",
            "consequence": "s >= (cot(pi/(2n))-1)/(C*sqrt(p)+1), hence s=Omega(sqrt(n)) when n is comparable to p.",
        },
        "status": {
            "elementary_fourier_reduction": "proved algebraically and replayed numerically",
            "elliptic_kummer_lang_sheaf_bound": "proof_obligation_not_yet_kernel_checked",
            "circuit_lower_bound": "not_claimed; high divisor support can still arise from a short nonlinear circuit",
        },
        "scientific_boundary": [
            "The result targets exact single-character rational evaluators and divisor support, not arbitrary arithmetic circuits.",
            "The numerical secp256k1 values use only fixed public curve parameters.",
            "No external point, unknown scalar, wallet or production discrete-log target is accepted.",
        ],
    }
    grammar = {
        "experiment": payload["experiment"],
        "formula": payload["elementary_identity"],
        "conditional_bridge": payload["conditional_bridge"],
    }
    payload["contract_sha256"] = hashlib.sha256(
        stable_json(grammar).encode()
    ).hexdigest()
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("experiments/uorc056/fourier_divisor_barrier_results.json"),
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = stable_json(run())
    if args.check:
        if args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("Fourier-divisor result artifact drifted")
    else:
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
