#!/usr/bin/env python3
"""Exact C45 full-field Ward near-period collapse.

This package uses only fixed public curves and known scalar indices. It accepts
no external target point, key, wallet, signature, nonce, or unknown production
scalar.

For a marked order-n point G let W_k=psi_k(G), let A,B be the Ward period
constants, and let Q=[k]G. Define the public raw section

    Phi(Q) = (psi_(p-1)(Q)/psi_(p-1+n)(Q))^(1/n^2 mod p-1)

and the full-field near-period channels

    R_a(Q)=psi_(n+a)(Q)/psi_a(Q).

The exact identity checked here is

    R_a(Q)=Phi(Q)^(-n(n+2a)).

Thus every offset a in the declared Ward family is only a public power of one
already-known field state. Varying the offset does not create a second
independent orientation channel.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

Point = Optional[tuple[int, int]]

SECP_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP_G = (
    0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
)
SECP_WARD_A = 0x96512C530B53BECF99A0CC5F16EB89A4C21AEF26F30180F962104448283F449F
SECP_WARD_B = 0x7015EAE8011C9350D55357787AA75CFC7A95382D5E54AA836B076F226E046953

TOY_CASES = (
    (43, 31, (2, 12), "frozen-small-1"),
    (79, 67, (1, 18), "frozen-small-2"),
    (151, 19, (70, 122), "frozen-small-3"),
    (907, 967, (2, 165), "frozen-medium-1"),
    (1087, 271, (1017, 688), "frozen-medium-2"),
    (1303, 1249, (1, 201), "frozen-medium-3"),
    (3571, 3469, (4, 1706), "frozen-large-1"),
    (3931, 4021, (4, 1427), "frozen-large-2"),
)
MAX_OFFSET = 8


def quadratic_character(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    return 1 if pow(value, (p - 1) // 2, p) == 1 else -1


def ec_add(left: Point, right: Point, p: int) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        slope = 3 * x1 * x1 * pow(2 * y1, -1, p) % p
    else:
        slope = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def ec_mul(scalar: int, point: Point, p: int) -> Point:
    result: Point = None
    addend = point
    while scalar:
        if scalar & 1:
            result = ec_add(result, addend, p)
        addend = ec_add(addend, addend, p)
        scalar >>= 1
    return result


def division_polynomial_evaluator(point: tuple[int, int], p: int):
    x, y = point

    @lru_cache(maxsize=None)
    def psi(index: int) -> int:
        if index < 0:
            return -psi(-index) % p
        if index == 0:
            return 0
        if index == 1:
            return 1
        if index == 2:
            return 2 * y % p
        if index == 3:
            return (3 * pow(x, 4, p) + 84 * x) % p
        if index == 4:
            return 4 * y * (pow(x, 6, p) + 140 * pow(x, 3, p) - 392) % p
        if index & 1:
            middle = (index - 1) // 2
            return (
                psi(middle + 2) * pow(psi(middle), 3, p)
                - psi(middle - 1) * pow(psi(middle + 1), 3, p)
            ) % p
        middle = index // 2
        return (
            psi(middle)
            * pow(2 * y, -1, p)
            * (
                psi(middle + 2) * pow(psi(middle - 1), 2, p)
                - psi(middle - 2) * pow(psi(middle + 1), 2, p)
            )
        ) % p

    return psi


def ward_constants(
    p: int, n: int, generator: tuple[int, int]
) -> tuple[int, int, Any]:
    psi = division_polynomial_evaluator(generator, p)
    w_n_plus_1 = psi(n + 1)
    w_n_plus_2 = psi(n + 2)
    if not w_n_plus_1 or not w_n_plus_2 or not psi(2):
        raise AssertionError("Ward constants are singular")
    ward_a = w_n_plus_2 * pow(psi(2) * w_n_plus_1 % p, -1, p) % p
    ward_b = w_n_plus_1 * pow(ward_a, -1, p) % p
    if w_n_plus_1 != ward_a * ward_b % p:
        raise AssertionError("W_(n+1)=A*B failed")
    if w_n_plus_2 != psi(2) * ward_a * ward_a % p * ward_b % p:
        raise AssertionError("W_(n+2)=W_2*A^2*B failed")
    return ward_a, ward_b, psi


def raw_section(
    point: tuple[int, int], p: int, n: int, root_exponent: int
) -> int:
    psi = division_polynomial_evaluator(point, p)
    numerator = psi(p - 1)
    denominator = psi(p - 1 + n)
    if not numerator or not denominator:
        raise AssertionError("raw section is singular")
    ratio = numerator * pow(denominator, -1, p) % p
    value = pow(ratio, root_exponent, p)
    if pow(value, n * n, p) != ratio:
        raise AssertionError("raw section root verification failed")
    return value


def scalar_sample(order: int, full: bool) -> list[int]:
    if full:
        return list(range(1, order))
    candidates = list(range(1, min(order, 25)))
    candidates.extend(
        value
        for value in (
            order // 3,
            order // 2,
            (2 * order) // 3,
            order - 3,
            order - 2,
            order - 1,
        )
        if 0 < value < order
    )
    return sorted(set(candidates))


def analyze_curve(
    p: int,
    n: int,
    generator: tuple[int, int],
    label: str,
    *,
    full_orbit: bool,
    fixed_ward: tuple[int, int] | None = None,
) -> dict[str, Any]:
    if (generator[1] * generator[1] - generator[0] ** 3 - 7) % p:
        raise AssertionError("generator is not on y^2=x^3+7")
    if ec_mul(n, generator, p) is not None:
        raise AssertionError("declared generator order failed")
    if math.gcd(n, p - 1) != 1:
        raise AssertionError("n-th powers are not invertible in F_p^*")

    ward_a, ward_b, base_psi = ward_constants(p, n, generator)
    if fixed_ward is not None and (ward_a, ward_b) != fixed_ward:
        raise AssertionError("fixed secp256k1 Ward constants changed")

    root_exponent = pow((n * n) % (p - 1), -1, p - 1)
    c = pow(ward_b, -root_exponent, p)
    if ward_a * pow(c, 2 * n, p) % p != 1:
        raise AssertionError("A*c^(2n)=1 failed")
    if ward_b * pow(c, n * n, p) % p != 1:
        raise AssertionError("B*c^(n^2)=1 failed")

    raw_checks = 0
    channel_checks = 0
    recurrence_checks = 0
    canonical_phase_checks = 0
    scalars = scalar_sample(n, full_orbit)

    for k in scalars:
        point = ec_mul(k, generator, p)
        if point is None:
            raise AssertionError("sampled nonzero scalar reached infinity")
        psi_q = division_polynomial_evaluator(point, p)
        phi = raw_section(point, p, n, root_exponent)
        expected_phi = base_psi(k) * pow(c, k * k, p) % p
        if phi != expected_phi:
            raise AssertionError("Phi([k]G)=W_k*c^(k^2) failed")
        raw_checks += 1

        channels: list[int] = []
        for offset in range(1, MAX_OFFSET + 1):
            denominator = psi_q(offset)
            if not denominator:
                raise AssertionError("near-period denominator vanished")
            observed = psi_q(n + offset) * pow(denominator, -1, p) % p
            predicted = pow(phi, -n * (n + 2 * offset), p)
            if observed != predicted:
                raise AssertionError("full-field Ward channel did not collapse to Phi")
            channels.append(observed)
            channel_checks += 1

        transition = channels[1] * pow(channels[0], -1, p) % p
        expected_transition = pow(phi, -2 * n, p)
        if transition != expected_transition:
            raise AssertionError("offset transition is not Phi^(-2n)")
        for left, right in zip(channels, channels[1:]):
            if right != transition * left % p:
                raise AssertionError("near-period channels are not geometric")
            recurrence_checks += 1

        if p % 4 == 3:
            canonical_root = pow(transition, (p + 1) // 4, p)
            if canonical_root * canonical_root % p != transition:
                raise AssertionError("canonical square root failed")
            residual = channels[0] * pow(
                pow(canonical_root, n + 2, p), -1, p
            ) % p
            expected_residual = quadratic_character(phi, p) % p
            if residual != expected_residual:
                raise AssertionError("residual phase is not chi(Phi)")
            canonical_phase_checks += 1

    return {
        "label": label,
        "p": p,
        "n": n,
        "generator": list(generator),
        "full_orbit": full_orbit,
        "sampled_scalars": len(scalars),
        "maximum_offset": MAX_OFFSET,
        "ward_a": ward_a,
        "ward_b": ward_b,
        "chi_c": quadratic_character(c, p),
        "raw_checks": raw_checks,
        "full_field_channel_checks": channel_checks,
        "offset_recurrence_checks": recurrence_checks,
        "canonical_phase_checks": canonical_phase_checks,
        "identities": {
            "ward_constants": True,
            "A_c_2n": True,
            "B_c_n2": True,
            "raw_equals_Wk_c_k2": True,
            "all_channels_are_raw_powers": True,
            "channels_form_one_geometric_family": True,
            "residual_phase_equals_chi_raw_when_p_mod_4_is_3": p % 4 == 3,
        },
        "errors": 0,
    }


def build_payload() -> dict[str, Any]:
    curves = [
        analyze_curve(p, n, generator, label, full_orbit=n <= 100)
        for p, n, generator, label in TOY_CASES
    ]
    secp = analyze_curve(
        SECP_P,
        SECP_N,
        SECP_G,
        "secp256k1-fixed-known-scalars",
        full_orbit=False,
        fixed_ward=(SECP_WARD_A, SECP_WARD_B),
    )
    if secp["chi_c"] != -1:
        raise AssertionError("secp raw generator phase must be -1")

    aggregate = {
        "toy_curves": len(curves),
        "secp_fixed_instance": 1,
        "sampled_scalars": sum(row["sampled_scalars"] for row in curves) + secp["sampled_scalars"],
        "raw_checks": sum(row["raw_checks"] for row in curves) + secp["raw_checks"],
        "full_field_channel_checks": sum(row["full_field_channel_checks"] for row in curves) + secp["full_field_channel_checks"],
        "offset_recurrence_checks": sum(row["offset_recurrence_checks"] for row in curves) + secp["offset_recurrence_checks"],
        "canonical_phase_checks": sum(row["canonical_phase_checks"] for row in curves) + secp["canonical_phase_checks"],
        "errors": 0,
    }

    payload: dict[str, Any] = {
        "profile_id": "UORC-056-FULL-FIELD-WARD-COLLAPSE-C45",
        "schema_version": "1.0",
        "central_target": "Y_G(x([k]G))/y([k]G)=(-1)^k",
        "scope": "fixed public toy curves and known scalar indices on fixed secp256k1; no external target or unknown production scalar",
        "main_identity": "psi_(n+a)(Q)/psi_a(Q) = Phi_raw(Q)^(-n*(n+2*a))",
        "raw_state_definition": "Phi_raw(Q)=(psi_(p-1)(Q)/psi_(p-1+n)(Q))^((n^2)^(-1) mod (p-1))",
        "consequences": {
            "all_offsets_are_powers_of_one_public_state": True,
            "offset_transition": "R_(a+1)(Q)/R_a(Q)=Phi_raw(Q)^(-2n)",
            "one_dimensional_geometric_family": True,
            "secp_residual_binary_phase": "chi(Phi_raw(Q))=(-1)^k*rho_G(Q)",
            "second_independent_ward_field_channel_found": False,
        },
        "curves": curves,
        "secp256k1": secp,
        "aggregate": aggregate,
        "decision": {
            "full_field_near_period_family_constructed": True,
            "full_field_near_period_family_collapses_to_raw_state": True,
            "varying_ward_offset_adds_independent_information": False,
            "raw_state_is_publicly_polylog_evaluable": True,
            "cheap_nonlinear_raw_state_decoder_found": False,
            "second_independent_open_section_found": False,
            "public_ordered_sector_evaluator_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
        "successor": {
            "id": "SECOND-INDEPENDENT-OPEN-SECTION-C46",
            "target": "construct a generator-sensitive unsquared section not generated by powers of Phi_raw, or a genuinely low-size nonlinear decoder of Phi_raw",
            "reject": "another Ward offset, ratio, product, or rational power that is already a function of Phi_raw alone",
        },
        "claim_boundary": [
            "The exact elliptic/division-polynomial replay uses public known scalar indices only.",
            "The all-offset identity follows from the Ward period law and division-polynomial composition; the executable replay covers the declared instances and offsets.",
            "This closes independence of the Ward near-period full-field family, not arbitrary nonlinear functions of Phi_raw.",
            "No theta, elliptic-unit, p-adic, modular-composition, or unrestricted arithmetic-circuit class is closed.",
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
        args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("UORC056_FULL_FIELD_WARD_COLLAPSE_C45_OK")
    print(json.dumps(payload["aggregate"], indent=2, sort_keys=True))
    print(json.dumps(payload["decision"], indent=2, sort_keys=True))
    print("digest=" + str(payload["digest"]))


if __name__ == "__main__":
    main()
