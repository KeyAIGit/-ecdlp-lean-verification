#!/usr/bin/env python3
"""Machine-readable decision package for UORC-056 C43."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from uorc056_c43_glv_dft_screen import build_dft_payload
from uorc056_c43_local_glv_branch import build_branch_payload

SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def build_payload() -> dict[str, Any]:
    branch = build_branch_payload()
    dft = build_dft_payload()
    glv_orbits = (SECP_N - 1) // 6
    half_kernel = (SECP_N - 1) // 2
    if half_kernel != 3 * glv_orbits:
        raise AssertionError("secp256k1 half-kernel is not three GLV blocks")

    payload: dict[str, Any] = {
        "profile_id": "UORC-056-LOCAL-GLV-GAUGE-BREAKING-C43",
        "schema_version": "1.0",
        "central_target": "Y_G(x([k]G))/y([k]G)=(-1)^k",
        "predecessor": "C42 oriented transposed-resultant boundary",
        "local_glv_branch_factorization": branch,
        "glv_dft_character_boundary": dft,
        "secp256k1_frontier": {
            "n": SECP_N,
            "half_kernel_degree": half_kernel,
            "glv_orbits": glv_orbits,
            "glv_orbits_bit_length": glv_orbits.bit_length(),
            "half_kernel_equals_three_glv_orbits": half_kernel == 3 * glv_orbits,
            "residual_gauge_after_granting_carry_root": (
                "Klein-four sign action per split GLV orbit"
            ),
            "anchor_scope": (
                "one anchor fixes one sign at one orbit; it does not supply the "
                "ordered sector sign at all other quotient roots"
            ),
        },
        "exact_algebraic_result": {
            "kernel": "K_H(X)=kappa(X^3)",
            "carry_root": (
                "C_G(T)=Y_G(X)Y_G(beta X)Y_G(beta^2 X), T=X^3"
            ),
            "carry_square": "C_G(T)^2=(T+7)^3 mod kappa(T)",
            "carry_value": "C_G(x(Q)^3)=g_G(Q)y(Q)^3",
            "sector_root": (
                "J_G(X)=Y_G(beta X)Y_G(beta^2 X)/(X^3+7)"
            ),
            "sector_square": "J_G(X)^2=1 mod K_H(X)",
            "reconstruction": (
                "Y_G(X)(X^3+7)=C_G(X^3)J_G(X) mod K_H(X)"
            ),
            "parity": "(-1)^k=g_G(Q)J_G(x(Q))",
        },
        "claim_boundary": {
            "proved_or_replayed": [
                "the exact carry-root/sector-root polynomial factorization",
                "the exact residual product-preserving sign gauge",
                "failure of every cyclic-invariant decoder to select an ordered sign",
                "arbitrary-product closure of the declared structural GLV-DFT character grammar on p=2137",
                "non-uniformity of freely fitted two-L0/two-f0 quartic characters",
                "five frozen and four held-out prime-order j=0 curves",
            ],
            "not_claimed": [
                "an unrestricted arithmetic-circuit lower bound",
                "an unrestricted character-product lower bound with arbitrary coefficients",
                "production-size coefficient density for secp256k1",
                "a parity oracle",
                "a sub-square-root ECDLP algorithm",
            ],
        },
        "decision": {
            "exact_glv_carry_root_found": True,
            "exact_sector_root_found": True,
            "exact_oriented_root_reconstruction_found": True,
            "cubic_norm_breaks_all_local_sign_gauge": False,
            "residual_klein_four_gauge_survives": True,
            "cyclic_invariant_can_decode_ordered_parity": False,
            "declared_structural_glv_dft_character_grammar_closed": True,
            "freely_fitted_quartic_is_uniform": False,
            "local_glv_gauge_breaking_evaluator_found": False,
            "cheap_parity_decoder_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
        "aggregate": {
            "curves": int(branch["aggregate"]["curves"]),
            "frozen_curves": int(branch["aggregate"]["frozen"]),
            "heldout_curves": int(branch["aggregate"]["heldout"]),
            "carry_value_checks": int(branch["aggregate"]["carry_value_checks"]),
            "declared_character_atoms": int(
                dft["aggregate"]["declared_character_atoms"]
            ),
            "valid_character_atoms": int(
                dft["aggregate"]["valid_character_atoms"]
            ),
            "decisive_p2137_all_targets_absent": bool(
                dft["aggregate"]["decisive_p2137_all_targets_absent"]
            ),
            "quartic_fits_p229": bool(dft["aggregate"]["quartic_fits_p229"]),
            "quartic_fits_p997": bool(dft["aggregate"]["quartic_fits_p997"]),
            "quartic_fails_p2137": bool(
                dft["aggregate"]["quartic_fails_p2137"]
            ),
            "errors": int(branch["aggregate"]["errors"])
            + int(dft["aggregate"]["errors"]),
        },
        "successor": {
            "id": "ORDERED-SECTOR-TRANSPORT-C44",
            "target": (
                "construct an unsquared public transport for the ordered sector "
                "J_G(x(Q)), rather than another cyclic norm or freely fitted character"
            ),
            "mandatory_gate": (
                "the mechanism must be anti-sensitive to the residual Klein-four "
                "gauge and must generate its coefficients without orbit enumeration"
            ),
        },
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
    print("UORC056_LOCAL_GLV_GAUGE_BREAKING_C43_OK")
    print(json.dumps(payload["aggregate"], indent=2, sort_keys=True))
    print("digest=" + str(payload["digest"]))


if __name__ == "__main__":
    main()
