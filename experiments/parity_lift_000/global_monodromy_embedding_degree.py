#!/usr/bin/env python3
"""Exact arithmetic certificate for GLOBAL-MONODROMY-SECTION-009.

The script accepts no input and targets no external point, key, wallet, or
discrete-log instance.  It certifies the least extension degree in which a
nontrivial multiplicative character of the secp256k1 prime-order subgroup can
take values in finite-field roots of unity.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Prime factorization of K = (N - 1) / 6.  The repository separately
# kernel-checks primality of N; this script verifies the order certificate.
K_FACTORS = (
    (2, 5),
    (149, 1),
    (631, 1),
    (107361793816595537, 1),
    (174723607534414371449, 1),
    (341948486974166000522343609283189, 1),
)


def factor_product() -> int:
    value = 1
    for prime, exponent in K_FACTORS:
        value *= prime**exponent
    return value


def build_payload() -> dict[str, object]:
    embedding_degree = (N - 1) // 6
    assert N - 1 == 6 * embedding_degree
    assert factor_product() == embedding_degree
    assert math.gcd(N, P - 1) == 1
    assert pow(P, embedding_degree, N) == 1

    reduction_witnesses: dict[str, str] = {}
    for prime, _ in K_FACTORS:
        witness = pow(P, embedding_degree // prime, N)
        if witness == 1:
            raise AssertionError(
                f"order certificate failed after division by prime {prime}"
            )
        reduction_witnesses[str(prime)] = hex(witness)

    sqrt_n = math.isqrt(N)
    extension_bits = embedding_degree * P.bit_length()

    return {
        "scope": (
            "fixed public secp256k1 parameters only; no external point or "
            "discrete-log target"
        ),
        "package": "GLOBAL-MONODROMY-SECTION-009",
        "p_hex": hex(P),
        "n_hex": hex(N),
        "gcd_n_p_minus_one": math.gcd(N, P - 1),
        "embedding_degree": embedding_degree,
        "embedding_degree_bit_length": embedding_degree.bit_length(),
        "embedding_degree_factorization": [
            {"prime": prime, "exponent": exponent}
            for prime, exponent in K_FACTORS
        ],
        "order_certificate": {
            "p_pow_k_mod_n": hex(pow(P, embedding_degree, N)),
            "p_pow_k_over_prime_mod_n": reduction_witnesses,
            "criterion": (
                "p^k=1 mod n and p^(k/q)!=1 mod n for every prime q|k"
            ),
        },
        "consequence": {
            "least_d_with_n_dividing_p_pow_d_minus_one": embedding_degree,
            "minimum_dense_representation_bits_for_one_F_p_pow_d_element": (
                extension_bits
            ),
            "embedding_degree_over_floor_sqrt_n": embedding_degree // sqrt_n,
            "embedding_degree_exceeds_sqrt_n_by_bits": (
                embedding_degree.bit_length() - sqrt_n.bit_length()
            ),
        },
        "interpretation": (
            "A nontrivial finite-field multiplicative character of the "
            "order-n subgroup requires mu_n and therefore F_(p^d) with d a "
            "multiple of this embedding degree.  Explicit extension-field "
            "representation alone is far above the generic square-root scale."
        ),
        "claim_boundary": [
            "This closes only finite-field root-of-unity monodromy mechanisms.",
            "It does not rule out a direct base-field weight-zero decoder.",
            "It does not construct an R3, carry, parity, or ECDLP oracle.",
        ],
    }


def main() -> None:
    output = Path(__file__).with_name(
        "global_monodromy_embedding_degree_results.json"
    )
    payload = build_payload()
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
