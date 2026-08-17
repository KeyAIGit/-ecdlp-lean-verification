#!/usr/bin/env python3
"""Exact C44 boundary for Ward-period open transport on secp256k1.

This package uses only public fixed secp256k1 constants and small, known
scalar indices. It accepts no external point, key, wallet, signature, nonce,
or unknown production target.

The result has two parts.

1. Every quadratic-character output of the declared Ward period-lattice
   transport belongs, up to a public global phase, to one of four classes:

       1, near(k), near(k+1), near(k) near(k+1),

   where near(k)=(-1)^k rho(k) and rho(k)=chi(psi_k(G)). Arbitrary finite
   products remain in the same four classes. Exact secp256k1 witnesses show
   that neither global phase of any class equals parity on all scalars.

2. Doubling together with the GLV multiplier has 32 cycles on the
   secp256k1 pair quotient. One public anchor fixes only one cycle, leaving
   31 independent binary orientation choices. A transitive public multiplier
   exists (7), but locating Q on its orbit is a multiplicative discrete-log
   localization problem; this is a reduction, not a lower bound.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
LAMBDA = 0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72
WARD_A = 0x96512C530B53BECF99A0CC5F16EB89A4C21AEF26F30180F962104448283F449F
WARD_B = 0x7015EAE8011C9350D55357787AA75CFC7A95382D5E54AA836B076F226E046953

N_MINUS_ONE_FACTORS: dict[int, int] = {
    2: 6,
    3: 1,
    149: 1,
    631: 1,
    107361793816595537: 1,
    174723607534414371449: 1,
    341948486974166000522343609283189: 1,
}


def quadratic_character(value: int, modulus: int = P) -> int:
    value %= modulus
    if value == 0:
        return 0
    return 1 if pow(value, (modulus - 1) // 2, modulus) == 1 else -1


@lru_cache(maxsize=None)
def psi(index: int) -> int:
    """Division-polynomial value psi_index(G), for the fixed public G."""
    if index < 0:
        return -psi(-index) % P
    if index == 0:
        return 0
    if index == 1:
        return 1
    if index == 2:
        return 2 * GY % P
    if index == 3:
        return (3 * pow(GX, 4, P) + 84 * GX) % P
    if index == 4:
        return 4 * GY * (pow(GX, 6, P) + 140 * pow(GX, 3, P) - 392) % P
    if index & 1:
        middle = (index - 1) // 2
        return (
            psi(middle + 2) * pow(psi(middle), 3, P)
            - psi(middle - 1) * pow(psi(middle + 1), 3, P)
        ) % P
    middle = index // 2
    return (
        psi(middle)
        * pow(2 * GY, -1, P)
        * (
            psi(middle + 2) * pow(psi(middle - 1), 2, P)
            - psi(middle - 2) * pow(psi(middle + 1), 2, P)
        )
    ) % P


def parity(index: int) -> int:
    return 1 if index % 2 == 0 else -1


def rho(index: int) -> int:
    result = quadratic_character(psi(index))
    if result == 0:
        raise AssertionError("psi_k(G) vanished at a declared nonzero small index")
    return result


def near(index: int) -> int:
    return parity(index) * rho(index)


def ward_class(alpha: int, beta: int, index: int) -> int:
    value = 1
    if alpha & 1:
        value *= near(index)
    if beta & 1:
        value *= near(index + 1)
    return value


def first_mismatch(alpha: int, beta: int, phase: int) -> int:
    for index in range(1, 65):
        if phase * ward_class(alpha, beta, index) != parity(index):
            return index
    raise AssertionError("declared class unexpectedly matched parity through 64")


def verify_exact_order(base: int, order: int, order_factors: dict[int, int]) -> None:
    if pow(base, order, N) != 1:
        raise AssertionError("candidate order does not annihilate the base")
    for prime in order_factors:
        if order % prime == 0 and pow(base, order // prime, N) == 1:
            raise AssertionError(f"candidate order is not exact; prime={prime}")


def build_payload() -> dict[str, Any]:
    if quadratic_character(WARD_A) != 1:
        raise AssertionError("Ward A must be a square on secp256k1")
    if quadratic_character(WARD_B) != -1:
        raise AssertionError("Ward B must be a nonsquare on secp256k1")

    class_rows: list[dict[str, Any]] = []
    for alpha in (0, 1):
        for beta in (0, 1):
            witnesses = {
                str(phase): first_mismatch(alpha, beta, phase)
                for phase in (-1, 1)
            }
            class_rows.append(
                {
                    "alpha": alpha,
                    "beta": beta,
                    "representative": (
                        "1"
                        if not alpha and not beta
                        else "near_k"
                        if alpha and not beta
                        else "near_k_plus_1"
                        if beta and not alpha
                        else "near_k*near_k_plus_1"
                    ),
                    "phase_mismatch_witnesses": witnesses,
                    "neither_global_phase_is_parity": True,
                }
            )

    small_values = [
        {
            "k": index,
            "rho": rho(index),
            "parity": parity(index),
            "near": near(index),
        }
        for index in range(1, 8)
    ]

    order_two = (N - 1) // 64
    order_two_factors = dict(N_MINUS_ONE_FACTORS)
    del order_two_factors[2]
    verify_exact_order(2, order_two, order_two_factors)

    if order_two % 3:
        raise AssertionError("order of two must contain the GLV order-three subgroup")
    if pow(2, 2 * (order_two // 3), N) != LAMBDA:
        raise AssertionError("GLV lambda is not the declared power of two")
    if pow(LAMBDA, 3, N) != 1 or LAMBDA == 1:
        raise AssertionError("lambda is not nontrivial order three")

    pair_components = (N - 1) // 2
    doubling_cycles = pair_components // order_two
    if doubling_cycles != 32:
        raise AssertionError("corrected doubling cycle count is not 32")

    verify_exact_order(7, N - 1, N_MINUS_ONE_FACTORS)
    pair_order_seven = (N - 1) // 2
    if pow(7, pair_order_seven, N) != N - 1:
        raise AssertionError("seven does not reach -1 at the half-order")

    payload: dict[str, Any] = {
        "profile_id": "UORC-056-WARD-OPEN-TRANSPORT-C44",
        "schema_version": "1.0",
        "central_target": "Y_G(x([k]G))/y([k]G)=(-1)^k",
        "scope": (
            "fixed public secp256k1 constants and known small scalar witnesses; "
            "no external target or unknown production scalar"
        ),
        "ward_character_normal_form": {
            "chi_A": quadratic_character(WARD_A),
            "chi_B": quadratic_character(WARD_B),
            "rho_definition": "rho(k)=chi(psi_k(G))",
            "near_definition": "near(k)=chi(psi_(n+1)([k]G))=(-1)^k*rho(k)",
            "atom_variable_class": "near(k)^alpha * near(k+1)^beta",
            "alpha_beta_domain": "{0,1}^2",
            "finite_products_stay_in_four_classes": True,
            "classes": class_rows,
            "small_exact_values": small_values,
            "all_finite_multiplicative_period_lattice_character_decoders_closed": True,
        },
        "multiplier_transport": {
            "order_of_two_mod_n": order_two,
            "order_of_two_bit_length": order_two.bit_length(),
            "lambda_equals_power_of_two": True,
            "lambda_power_exponent": 2 * (order_two // 3),
            "pair_quotient_components": pair_components,
            "doubling_glv_cycles": doubling_cycles,
            "one_public_anchor_leaves_free_cycle_signs": doubling_cycles - 1,
            "number_of_residual_anchor_assignments": 2 ** (doubling_cycles - 1),
            "transitive_public_multiplier": 7,
            "order_of_seven_mod_n": N - 1,
            "order_of_seven_on_pair_quotient": pair_order_seven,
            "seven_pair_action_transitive": True,
            "localization_boundary": (
                "using a transitive multiplier still requires locating Q=+-[7^t]G "
                "or evaluating an anchor-to-query open transport directly"
            ),
        },
        "decision": {
            "ward_period_lattice_multiplicative_character_algorithm_found": False,
            "ward_period_lattice_multiplicative_character_class_closed": True,
            "doubling_and_glv_select_global_ordered_sector": False,
            "transitive_multiplier_exists": True,
            "cheap_orbit_localization_found": False,
            "public_ordered_sector_evaluator_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
        "successor": {
            "id": "FULL-FIELD-OPEN-ROOT-TRANSPORT-C45",
            "target": (
                "construct one unsquared anchor-to-query field transport whose value "
                "retains orientation before any quadratic character, norm, square, "
                "closed loop, or orbit-index localization"
            ),
            "reject": (
                "any candidate that reduces to a finite monomial in Ward near-period "
                "characters or requires the hidden multiplier-orbit exponent"
            ),
        },
        "claim_boundary": [
            "The four-class closure is for the declared multiplicative quadratic-character period-lattice grammar.",
            "The cycle counts and order certificates are exact fixed secp256k1 arithmetic.",
            "The multiplier-localization statement is a reduction, not an unconditional complexity lower bound.",
            "No unrestricted full-field Miller, theta, elliptic-unit, p-adic, or arithmetic-circuit class is closed.",
        ],
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["digest"] = hashlib.sha256(raw).hexdigest()
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    payload = build_payload()
    if args.out:
        args.out.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print("UORC056_WARD_OPEN_TRANSPORT_C44_OK")
    print(json.dumps(payload["decision"], indent=2, sort_keys=True))
    print("digest=" + str(payload["digest"]))


if __name__ == "__main__":
    main()
