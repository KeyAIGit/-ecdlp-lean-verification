#!/usr/bin/env python3
"""Exact C47 collapse of the GLV raw-state triple to one field coordinate.

The public raw section Phi_raw was constructed in C45. On a j=0 curve with
CM automorphism alpha(x,y)=(beta*x,y), this package verifies

    Phi_raw(alpha Q)   = beta   * Phi_raw(Q),
    Phi_raw(alpha^2 Q) = beta^2 * Phi_raw(Q).

Hence the three seemingly different full-field sensors are one sensor with two
known public rescalings. The package uses only public toy curves and known
scalar indices on fixed secp256k1. It accepts no external target, key, wallet,
signature, nonce, or unknown production scalar.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from uorc056_full_field_ward_collapse_c45 import (
    SECP_G,
    SECP_N,
    SECP_P,
    TOY_CASES,
    ec_mul,
    raw_section,
    scalar_sample,
)

SECP_BETA = 0x7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE
SECP_LAMBDA = 0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72


def least_nontrivial_cube_root(p: int) -> int:
    for beta in range(2, p):
        if (beta * beta + beta + 1) % p == 0:
            return beta
    raise AssertionError("field has no nontrivial cube root of unity")


def glv_eigenvalue(
    p: int, n: int, generator: tuple[int, int], beta: int
) -> int:
    target = (beta * generator[0] % p, generator[1])
    for scalar in range(1, n):
        if ec_mul(scalar, generator, p) == target:
            return scalar
    raise AssertionError("CM image is not on the declared generated subgroup")


def cm_weight(index: int) -> int:
    """Exponent e in psi_index(beta*x,y)=beta^e psi_index(x,y), modulo 3."""
    return 1 if index % 3 == 0 else 0


def analyze_curve(
    p: int,
    n: int,
    generator: tuple[int, int],
    label: str,
    *,
    full_orbit: bool,
    fixed_beta: int | None = None,
    fixed_lambda: int | None = None,
) -> dict[str, Any]:
    beta = fixed_beta if fixed_beta is not None else least_nontrivial_cube_root(p)
    if pow(beta, 3, p) != 1 or beta == 1:
        raise AssertionError("beta is not a nontrivial cube root")
    lam = (
        fixed_lambda
        if fixed_lambda is not None
        else glv_eigenvalue(p, n, generator, beta)
    )
    if (lam * lam + lam + 1) % n:
        raise AssertionError("lambda does not satisfy lambda^2+lambda+1=0")
    if ec_mul(lam, generator, p) != (beta * generator[0] % p, generator[1]):
        raise AssertionError("declared GLV eigenvalue failed")

    if (p - 1) % 3 != 0:
        raise AssertionError("p-1 is not divisible by three")
    if n % 3 != 1:
        raise AssertionError("declared order is not 1 modulo three")
    if cm_weight(p - 1) != 1:
        raise AssertionError("raw numerator does not have CM weight one")
    if cm_weight(p - 1 + n) != 0:
        raise AssertionError("raw denominator does not have CM weight zero")

    root_exponent = pow((n * n) % (p - 1), -1, p - 1)
    if root_exponent % 3 != 1:
        raise AssertionError("raw root exponent does not preserve beta")

    scalars = scalar_sample(n, full_orbit)
    first_rotation_checks = 0
    second_rotation_checks = 0
    point_action_checks = 0
    fourier_checks = 0
    product_checks = 0
    ratio_checks = 0

    for k in scalars:
        q = ec_mul(k, generator, p)
        if q is None:
            raise AssertionError("sampled nonzero scalar reached infinity")
        alpha_q = (beta * q[0] % p, q[1])
        alpha2_q = (beta * beta * q[0] % p, q[1])
        if alpha_q != ec_mul((lam * k) % n, generator, p):
            raise AssertionError("alpha Q does not equal [lambda k]G")
        if alpha2_q != ec_mul((lam * lam * k) % n, generator, p):
            raise AssertionError("alpha^2 Q does not equal [lambda^2 k]G")
        point_action_checks += 2

        phi0 = raw_section(q, p, n, root_exponent)
        phi1 = raw_section(alpha_q, p, n, root_exponent)
        phi2 = raw_section(alpha2_q, p, n, root_exponent)

        if phi1 != beta * phi0 % p:
            raise AssertionError("Phi(alpha Q) != beta*Phi(Q)")
        first_rotation_checks += 1
        if phi2 != beta * beta * phi0 % p:
            raise AssertionError("Phi(alpha^2 Q) != beta^2*Phi(Q)")
        second_rotation_checks += 1

        if phi1 * pow(phi0, -1, p) % p != beta:
            raise AssertionError("first GLV ratio is not public beta")
        if phi2 * pow(phi0, -1, p) % p != beta * beta % p:
            raise AssertionError("second GLV ratio is not public beta^2")
        ratio_checks += 2

        mode0 = (phi0 + phi1 + phi2) % p
        mode1 = (phi0 + beta * beta * phi1 + beta * phi2) % p
        mode2 = (phi0 + beta * phi1 + beta * beta * phi2) % p
        if mode0 != 0 or mode1 != 3 * phi0 % p or mode2 != 0:
            raise AssertionError("GLV Fourier triple did not collapse to one mode")
        fourier_checks += 3

        if phi0 * phi1 % p * phi2 % p != pow(phi0, 3, p):
            raise AssertionError("GLV triple product is not Phi(Q)^3")
        product_checks += 1

    return {
        "label": label,
        "p": p,
        "n": n,
        "generator": list(generator),
        "beta": beta,
        "lambda": lam,
        "full_orbit": full_orbit,
        "sampled_scalars": len(scalars),
        "cm_weight_numerator": cm_weight(p - 1),
        "cm_weight_denominator": cm_weight(p - 1 + n),
        "root_exponent_mod_3": root_exponent % 3,
        "point_action_checks": point_action_checks,
        "first_rotation_checks": first_rotation_checks,
        "second_rotation_checks": second_rotation_checks,
        "ratio_checks": ratio_checks,
        "fourier_checks": fourier_checks,
        "product_checks": product_checks,
        "identities": {
            "phi_alpha": "Phi(alpha Q)=beta*Phi(Q)",
            "phi_alpha2": "Phi(alpha^2 Q)=beta^2*Phi(Q)",
            "glv_triple_rank_one": True,
            "mode0_zero": True,
            "mode1_equals_three_phi": True,
            "mode2_zero": True,
            "triple_product_equals_phi_cubed": True,
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
        fixed_beta=SECP_BETA,
        fixed_lambda=SECP_LAMBDA,
    )
    rows = curves + [secp]
    aggregate = {
        "toy_curves": len(curves),
        "secp_fixed_instance": 1,
        "sampled_scalars": sum(row["sampled_scalars"] for row in rows),
        "point_action_checks": sum(row["point_action_checks"] for row in rows),
        "first_rotation_checks": sum(row["first_rotation_checks"] for row in rows),
        "second_rotation_checks": sum(row["second_rotation_checks"] for row in rows),
        "ratio_checks": sum(row["ratio_checks"] for row in rows),
        "fourier_checks": sum(row["fourier_checks"] for row in rows),
        "product_checks": sum(row["product_checks"] for row in rows),
        "errors": 0,
    }

    payload: dict[str, Any] = {
        "profile_id": "UORC-056-GLV-RAW-TRIPLE-COLLAPSE-C47",
        "schema_version": "1.0",
        "central_target": "Y_G(x([k]G))/y([k]G)=(-1)^k",
        "scope": (
            "fixed public toy curves and known scalar indices on fixed secp256k1; "
            "no external target or unknown production scalar"
        ),
        "main_identities": [
            "Phi_raw(alpha Q)=beta*Phi_raw(Q)",
            "Phi_raw(alpha^2 Q)=beta^2*Phi_raw(Q)",
            "(Phi0,Phi1,Phi2)=Phi0*(1,beta,beta^2)",
        ],
        "cm_weight_rule": (
            "psi_m(beta*x,y)=beta*psi_m(x,y) when 3 divides m, "
            "and equals psi_m(x,y) otherwise"
        ),
        "field_generation": (
            "the public field generated by the GLV triple equals the public field "
            "generated by Phi_raw(Q) alone"
        ),
        "fourier_normal_form": {
            "mode0": 0,
            "mode1": "3*Phi_raw(Q)",
            "mode2": 0,
        },
        "curves": curves,
        "secp256k1": secp,
        "aggregate": aggregate,
        "decision": {
            "glv_raw_triple_publicly_polylog_evaluable": True,
            "glv_raw_triple_has_three_independent_coordinates": False,
            "glv_raw_triple_collapses_to_one_raw_state": True,
            "glv_fourier_mixed_weight_decoder_found": False,
            "second_independent_open_section_found": False,
            "cheap_nonlinear_raw_state_decoder_found": False,
            "public_ordered_sector_evaluator_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
        "successor": {
            "id": "NON-WARD-INDEPENDENT-SECTION-C48",
            "target": (
                "leave the Ward/raw/geometric-jet family and construct a section with "
                "a genuinely independent transformation law, first from the p-adic "
                "arithmetic jet or an unsquared theta/elliptic-unit value"
            ),
            "reject": (
                "any GLV rotation, Ward offset, geometric first jet, product, ratio, "
                "or Fourier mode generated by Phi_raw alone"
            ),
        },
        "claim_boundary": [
            "The CM weight rule follows from the standard division-polynomial recurrence on j=0 curves; exact pointwise replay is included for the declared instances.",
            "The GLV triple adds no independent field coordinate, but arbitrary nonlinear decoding of Phi_raw itself remains open.",
            "This package does not close the p-adic arithmetic jet, higher jets, theta functions, elliptic units, or unrestricted arithmetic circuits.",
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
    print("UORC056_GLV_RAW_TRIPLE_COLLAPSE_C47_OK")
    print(json.dumps(payload["aggregate"], indent=2, sort_keys=True))
    print(json.dumps(payload["decision"], indent=2, sort_keys=True))
    print("digest=" + str(payload["digest"]))


if __name__ == "__main__":
    main()
