#!/usr/bin/env python3
"""Exact and toy-only screen for GLOBAL-MONODROMY-SECTION-009.

This script verifies the cyclotomic GLV-carry identity

    sign(Im prod_{j=0}^2 (1-zeta_n^(lambda^j k))) = (-1)^gamma,

where the canonical representatives k_j satisfy

    k_0+k_1+k_2 = gamma*n, gamma in {1,2}.

It also certifies the multiplicative order of the secp256k1 field prime p
modulo the subgroup order n. No external point, key, wallet, or production
DLP target is accepted.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import mpmath as mp
from sympy import isprime

FROZEN_CASES = (
    (31, 25),
    (67, 29),
    (19, 7),
    (547, 506),
    (967, 824),
    (1093, 151),
    (271, 242),
    (1249, 93),
    (433, 198),
    (571, 461),
    (367, 283),
    (397, 362),
    (811, 130),
    (3469, 1683),
    (4021, 1812),
)

SECP_P = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16
)
SECP_N = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16
)
SECP_LAMBDA = int(
    "5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72",
    16,
)

EMBEDDING_DEGREE_FACTORS = {
    2: 5,
    149: 1,
    631: 1,
    107361793816595537: 1,
    174723607534414371449: 1,
    341948486974166000522343609283189: 1,
}


@dataclass(frozen=True)
class ToyCase:
    order: int
    lam: int
    points_checked: int
    phase_mismatches: int
    pure_imaginary_failures: int
    glv_invariance_failures: int
    anti_kummer_failures: int
    minimum_abs_imaginary_part: str
    maximum_relative_real_part: str


def sign_int(value: mp.mpf) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def run_toy_case(order: int, lam: int) -> ToyCase:
    if not isprime(order):
        raise AssertionError("toy subgroup order must be prime")
    if lam in (0, 1) or pow(lam, 3, order) != 1:
        raise AssertionError("lambda must have exact order three")

    mp.mp.dps = 100
    zeta = mp.e ** (2j * mp.pi / order)
    mismatches = 0
    pure_failures = 0
    glv_failures = 0
    anti_failures = 0
    min_abs_imag = mp.inf
    max_relative_real = mp.mpf("0")

    for scalar in range(1, order):
        reps = (
            scalar,
            lam * scalar % order,
            lam * lam * scalar % order,
        )
        total = sum(reps)
        if total not in (order, 2 * order):
            raise AssertionError("canonical GLV representatives do not sum to n or 2n")
        gamma = total // order
        expected = -1 if gamma == 1 else 1

        phase = mp.mpc(1)
        for exponent in reps:
            phase *= 1 - zeta**exponent

        observed = sign_int(mp.im(phase))
        mismatches += observed != expected
        min_abs_imag = min(min_abs_imag, abs(mp.im(phase)))
        relative_real = abs(mp.re(phase)) / max(abs(mp.im(phase)), mp.mpf("1e-90"))
        max_relative_real = max(max_relative_real, relative_real)
        pure_failures += relative_real > mp.mpf("1e-80")

        rotated = lam * scalar % order
        rotated_reps = (
            rotated,
            lam * rotated % order,
            lam * lam * rotated % order,
        )
        rotated_gamma = sum(rotated_reps) // order
        glv_failures += ((-1 if rotated_gamma == 1 else 1) != expected)

        negated = order - scalar
        negated_reps = (
            negated,
            lam * negated % order,
            lam * lam * negated % order,
        )
        negated_gamma = sum(negated_reps) // order
        anti_failures += ((-1 if negated_gamma == 1 else 1) != -expected)

    return ToyCase(
        order=order,
        lam=lam,
        points_checked=order - 1,
        phase_mismatches=mismatches,
        pure_imaginary_failures=pure_failures,
        glv_invariance_failures=glv_failures,
        anti_kummer_failures=anti_failures,
        minimum_abs_imaginary_part=mp.nstr(min_abs_imag, 30),
        maximum_relative_real_part=mp.nstr(max_relative_real, 8),
    )


def certify_embedding_degree() -> dict[str, object]:
    degree = (SECP_N - 1) // 6
    reconstructed = 1
    factor_rows = []
    for prime, exponent in EMBEDDING_DEGREE_FACTORS.items():
        if not isprime(prime):
            raise AssertionError(f"non-prime factor in certificate: {prime}")
        reconstructed *= prime**exponent
        residue = pow(SECP_P, degree // prime, SECP_N)
        if residue == 1:
            raise AssertionError("candidate embedding degree is not minimal")
        factor_rows.append(
            {
                "prime": prime,
                "exponent": exponent,
                "p_pow_degree_over_prime_mod_n": residue,
            }
        )

    if reconstructed != degree:
        raise AssertionError("embedding-degree factorization does not reconstruct")
    if pow(SECP_P, degree, SECP_N) != 1:
        raise AssertionError("p^degree != 1 mod n")
    if pow(SECP_P, degree // 2, SECP_N) != SECP_N - 1:
        raise AssertionError("half-Frobenius is not complex conjugation on mu_n")
    if (SECP_LAMBDA * SECP_LAMBDA + SECP_LAMBDA + 1) % SECP_N:
        raise AssertionError("secp256k1 lambda relation failed")

    return {
        "p": SECP_P,
        "n": SECP_N,
        "lambda": SECP_LAMBDA,
        "embedding_degree": degree,
        "embedding_degree_factorization": factor_rows,
        "p_pow_degree_mod_n": 1,
        "p_pow_half_degree_mod_n": SECP_N - 1,
        "embedding_degree_log2": math.log2(degree),
        "sqrt_n_log2": math.log2(SECP_N) / 2,
        "explicit_extension_over_sqrt_n_log2_ratio": (
            math.log2(degree) - math.log2(SECP_N) / 2
        ),
        "gcd_embedding_degree_with_three": math.gcd(degree, 3),
        "interpretation": (
            "An explicit Weil/Tate-pairing realization of the cyclotomic phase "
            "requires an n-th-root-of-unity field of degree ord_n(p)=(n-1)/6."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("global_monodromy_section_results.json"),
    )
    args = parser.parse_args()

    toy = [run_toy_case(order, lam) for order, lam in FROZEN_CASES]
    embedding = certify_embedding_degree()
    payload = {
        "package": "GLOBAL-MONODROMY-SECTION-009",
        "scope": (
            "exact scalar identities, fifteen frozen toy GLV groups, and fixed "
            "secp256k1 arithmetic only; no external or production target"
        ),
        "cyclotomic_section": (
            "M(k)=prod_{j=0}^2(1-zeta_n^(lambda^j*k)); "
            "sign(Im M(k))=(-1)^gamma"
        ),
        "proof_skeleton": [
            "1-zeta^a=-2*i*zeta^(a/2)*sin(pi*a/n) for 0<a<n",
            "all three sine factors are positive for canonical representatives",
            "sum of representatives is gamma*n with gamma in {1,2}",
            "therefore M(k)=8*i*(-1)^gamma*product(sin(pi*k_j/n))",
        ],
        "toy_cases": [asdict(case) for case in toy],
        "toy_aggregate": {
            "cases": len(toy),
            "points_checked": sum(case.points_checked for case in toy),
            "phase_mismatches": sum(case.phase_mismatches for case in toy),
            "pure_imaginary_failures": sum(
                case.pure_imaginary_failures for case in toy
            ),
            "glv_invariance_failures": sum(
                case.glv_invariance_failures for case in toy
            ),
            "anti_kummer_failures": sum(
                case.anti_kummer_failures for case in toy
            ),
        },
        "secp256k1_embedding_certificate": embedding,
        "route_decisions": {
            "universal_cyclotomic_cover": (
                "exact carry decoder exists once zeta_n^k is available"
            ),
            "pairing": (
                "not sub-sqrt in explicit representation: independent n-torsion "
                "and mu_n require extension degree (n-1)/6"
            ),
            "glv_self_pairing": (
                "degenerate because phi(Q)=[lambda]Q lies on the same n-torsion line"
            ),
            "frobenius_trace_norm": (
                "half-Frobenius sends M to -M; odd traces vanish and norms/squares "
                "discard the sign"
            ),
            "standard_theta_level": (
                "translation by an order-n point on one theta space requires level/degree "
                "divisible by n, so the explicit representation is at least n-dimensional"
            ),
            "p_adic": (
                "prime-to-p torsion has zero formal logarithm; adjoining mu_n has the same "
                "unramified degree ord_n(p)"
            ),
        },
        "public_carry_decoder_found": False,
        "public_R3_decoder_found": False,
        "unconditional_sub_sqrt_algorithm_found": False,
        "claim_boundary": [
            "The cyclotomic phase identity is exact.",
            "The embedding-degree certificate is exact for the fixed secp256k1 constants.",
            "The route decisions are scoped to explicit pairing, standard theta-level, "
            "Frobenius trace/norm, and formal-logarithm realizations.",
            "No universal impossibility theorem for arbitrary algorithms is claimed.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
