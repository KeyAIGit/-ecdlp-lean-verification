#!/usr/bin/env python3
"""Exact C46 collapse of the geometric first n-division jet to Phi_raw.

The geometric jet is

    J_n(Q)=2*y(Q)*(d/dx psi_n)(Q),

computed along the curve y^2=x^3+7 by first-order dual arithmetic. On every
declared public point Q=[k]G the package checks

    J_n(Q) = -n * Phi_raw(Q)^(-n^2).

Therefore the most natural first derivative of the order-n division condition
is not a second independent orientation section; it is one fixed public power
of the C45 raw state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from uorc056_full_field_ward_collapse_c45 import (
    SECP_G,
    SECP_N,
    SECP_P,
    SECP_WARD_A,
    SECP_WARD_B,
    TOY_CASES,
    division_polynomial_evaluator,
    ec_mul,
    quadratic_character,
    raw_section,
    scalar_sample,
    ward_constants,
)


class Dual:
    __slots__ = ("constant", "linear", "p")

    def __init__(self, constant: int, linear: int, p: int):
        self.constant = constant % p
        self.linear = linear % p
        self.p = p

    def coerce(self, other: Any) -> "Dual":
        if isinstance(other, Dual):
            if other.p != self.p:
                raise ValueError("dual field mismatch")
            return other
        return Dual(int(other), 0, self.p)

    def __add__(self, other: Any) -> "Dual":
        other = self.coerce(other)
        return Dual(self.constant + other.constant, self.linear + other.linear, self.p)

    __radd__ = __add__

    def __neg__(self) -> "Dual":
        return Dual(-self.constant, -self.linear, self.p)

    def __sub__(self, other: Any) -> "Dual":
        return self + (-self.coerce(other))

    def __rsub__(self, other: Any) -> "Dual":
        return self.coerce(other) - self

    def __mul__(self, other: Any) -> "Dual":
        other = self.coerce(other)
        return Dual(
            self.constant * other.constant,
            self.constant * other.linear + self.linear * other.constant,
            self.p,
        )

    __rmul__ = __mul__

    def inverse(self) -> "Dual":
        inverse_constant = pow(self.constant, -1, self.p)
        return Dual(
            inverse_constant,
            -self.linear * inverse_constant * inverse_constant,
            self.p,
        )

    def __truediv__(self, other: Any) -> "Dual":
        return self * self.coerce(other).inverse()

    def __pow__(self, exponent: int) -> "Dual":
        if exponent < 0:
            return self.inverse() ** (-exponent)
        result = Dual(1, 0, self.p)
        base = self
        while exponent:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent >>= 1
        return result


def geometric_first_jet(point: tuple[int, int], p: int, n: int) -> int:
    x0, y0 = point
    x = Dual(x0, 1, p)
    y_linear = 3 * x0 * x0 * pow(2 * y0, -1, p) % p
    y = Dual(y0, y_linear, p)

    @lru_cache(maxsize=None)
    def psi(index: int) -> Dual:
        if index < 0:
            return -psi(-index)
        if index == 0:
            return Dual(0, 0, p)
        if index == 1:
            return Dual(1, 0, p)
        if index == 2:
            return 2 * y
        if index == 3:
            return 3 * x**4 + 84 * x
        if index == 4:
            return 4 * y * (x**6 + 140 * x**3 - 392)
        if index & 1:
            middle = (index - 1) // 2
            return (
                psi(middle + 2) * psi(middle) ** 3
                - psi(middle - 1) * psi(middle + 1) ** 3
            )
        middle = index // 2
        return (
            psi(middle)
            / (2 * y)
            * (
                psi(middle + 2) * psi(middle - 1) ** 2
                - psi(middle - 2) * psi(middle + 1) ** 2
            )
        )

    value = psi(n)
    if value.constant:
        raise AssertionError("psi_n did not vanish at the order-n point")
    return 2 * y0 * value.linear % p


def analyze_curve(
    p: int,
    n: int,
    generator: tuple[int, int],
    label: str,
    *,
    full_orbit: bool,
    fixed_ward: tuple[int, int] | None = None,
) -> dict[str, Any]:
    ward_a, ward_b, base_psi = ward_constants(p, n, generator)
    if fixed_ward is not None and (ward_a, ward_b) != fixed_ward:
        raise AssertionError("fixed Ward constants changed")
    root_exponent = pow((n * n) % (p - 1), -1, p - 1)

    generator_jet = geometric_first_jet(generator, p, n)
    if generator_jet != (-n * ward_b) % p:
        raise AssertionError("J_n(G)=-n*B failed")

    scalars = scalar_sample(n, full_orbit)
    raw_collapse_checks = 0
    composition_checks = 0
    character_checks = 0

    for k in scalars:
        point = ec_mul(k, generator, p)
        if point is None:
            raise AssertionError("nonzero sampled scalar reached infinity")
        phi = raw_section(point, p, n, root_exponent)
        jet = geometric_first_jet(point, p, n)

        predicted_from_raw = -n * pow(phi, -n * n, p) % p
        if jet != predicted_from_raw:
            raise AssertionError("first jet is not -n*Phi_raw^(-n^2)")
        raw_collapse_checks += 1

        sign = -1 if (k - 1) & 1 else 1
        predicted_from_composition = (
            sign
            * pow(n % p, 1 - k * k, p)
            * pow(generator_jet, k * k, p)
            * pow(base_psi(k), -n * n, p)
        ) % p
        if jet != predicted_from_composition:
            raise AssertionError("first-jet composition identity failed")
        composition_checks += 1

        expected_character = quadratic_character(-n, p) * quadratic_character(phi, p)
        if quadratic_character(jet, p) != expected_character:
            raise AssertionError("first-jet character is not the raw character up to phase")
        character_checks += 1

    return {
        "label": label,
        "p": p,
        "n": n,
        "generator": list(generator),
        "full_orbit": full_orbit,
        "sampled_scalars": len(scalars),
        "ward_a": ward_a,
        "ward_b": ward_b,
        "generator_jet": generator_jet,
        "chi_minus_n": quadratic_character(-n, p),
        "generator_identity": "J_n(G)=-n*B",
        "raw_collapse_checks": raw_collapse_checks,
        "composition_checks": composition_checks,
        "character_checks": character_checks,
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
    rows = curves + [secp]
    aggregate = {
        "toy_curves": len(curves),
        "secp_fixed_instance": 1,
        "sampled_scalars": sum(row["sampled_scalars"] for row in rows),
        "generator_jet_checks": len(rows),
        "raw_collapse_checks": sum(row["raw_collapse_checks"] for row in rows),
        "composition_checks": sum(row["composition_checks"] for row in rows),
        "character_checks": sum(row["character_checks"] for row in rows),
        "errors": 0,
    }
    payload: dict[str, Any] = {
        "profile_id": "UORC-056-FIRST-JET-RAW-COLLAPSE-C46",
        "schema_version": "1.0",
        "central_target": "Y_G(x([k]G))/y([k]G)=(-1)^k",
        "scope": (
            "fixed public toy curves and known scalar indices on fixed secp256k1; "
            "no external target or unknown production scalar"
        ),
        "jet_definition": "J_n(Q)=2*y(Q)*(d/dx psi_n)(Q)",
        "generator_identity": "J_n(G)=-n*B",
        "main_identity": "J_n(Q)=-n*Phi_raw(Q)^(-n^2)",
        "character_identity": "chi(J_n(Q))=chi(-n)*chi(Phi_raw(Q))",
        "curves": curves,
        "secp256k1": secp,
        "aggregate": aggregate,
        "decision": {
            "geometric_first_jet_publicly_polylog_evaluable": True,
            "geometric_first_jet_collapses_to_raw_state": True,
            "geometric_first_jet_is_independent_open_section": False,
            "p_adic_arithmetic_jet_closed_by_this_package": False,
            "second_independent_open_section_found": False,
            "public_ordered_sector_evaluator_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
        "successor": {
            "id": "GLV-RAW-TRIPLE-OR-INDEPENDENT-SECTION-C47",
            "target": (
                "test the joint full-field state Phi_raw(Q), Phi_raw(alpha Q), "
                "Phi_raw(alpha^2 Q), and independently transforming theta/p-adic sections"
            ),
            "reject": (
                "any geometric first-jet, Ward-offset, or multiplicative derivative "
                "that reduces to a public power of Phi_raw"
            ),
        },
        "claim_boundary": [
            "The ordinary geometric first jet is distinct from the p-adic arithmetic jet of the lifted division condition.",
            "The executable replay checks the division-polynomial dual recurrence exactly on the declared public points.",
            "This package does not close higher jets, nonlinear functions of Phi_raw, GLV triples, theta functions, elliptic units, or unrestricted circuits.",
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
    print("UORC056_FIRST_JET_RAW_COLLAPSE_C46_OK")
    print(json.dumps(payload["aggregate"], indent=2, sort_keys=True))
    print(json.dumps(payload["decision"], indent=2, sort_keys=True))
    print("digest=" + str(payload["digest"]))


if __name__ == "__main__":
    main()
