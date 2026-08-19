#!/usr/bin/env python3
"""Exact arithmetic core for UORC-056 C53.

Only public synthetic curves and public scalar labels used for replay are
accepted.  No external target, private key, wallet, or hidden tangent advice is
read.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from uorc056_c52_deformation_core import (
    ALL_CURVES as C52_CURVES,
    Curve,
    quadratic_character,
    point_count,
    is_prime,
    torsion_lift_basis,
)

NEW_HELD_OUT = (
    (1051, 1093, (3, 385), 180, 941),
    (1237, 1279, (4, 599), 300, 504),
    (1249, 1303, (1, 100), 93, 1207),
    (1669, 1663, (2, 286), 248, 1344),
)
ALL_CURVES = C52_CURVES + NEW_HELD_OUT

SECP_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP_G = (
    55066263022277343669578718895168534326250603453777594175500187360389116729240,
    32670510020758816978083085130507043184471273380659243275938904335757337482424,
)
SECP_BETA = int(
    "7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE", 16
)
SECP_LAMBDA = int(
    "5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72", 16
)


def defect(connection_at_image: int, multiplier: int, connection_at_source: int, p: int) -> int:
    """Vertical scalar of Delta_m^nabla(P)=c([m]P)-m c(P)."""
    return (connection_at_image - multiplier * connection_at_source) % p


def recover_multiplier_from_defect(
    connection_at_image: int,
    defect_value: int,
    connection_at_source: int,
    p: int,
) -> int:
    if connection_at_source % p == 0:
        raise ZeroDivisionError("zero anchor connection does not reveal multiplier")
    return (
        (connection_at_image - defect_value)
        * pow(connection_at_source, -1, p)
    ) % p


def gauge_difference(
    gauge_at_image: int,
    multiplier: int,
    gauge_at_source: int,
    p: int,
) -> int:
    return defect(gauge_at_image, multiplier, gauge_at_source, p)


def connection_cocycle_rhs(
    delta_a_at_bP: int,
    a: int,
    delta_b_at_P: int,
    p: int,
) -> int:
    return (delta_a_at_bP + a * delta_b_at_P) % p


@dataclass(frozen=True)
class StateRow:
    k: int
    point: tuple[int, int]
    ua: int
    va: int
    ub: int
    vb: int
    omega_a: int
    omega_b: int
    det_ab: int
    position_a: int
    cm_t: int
    cm_r: int
    cm_s: int


def verify_fixture(row: tuple[int, int, tuple[int, int], int, int]) -> None:
    p, n, generator, beta, lam = row
    curve = Curve(p)
    if not is_prime(p) or not is_prime(n):
        raise AssertionError("fixture moduli are not prime")
    if point_count(curve) != n:
        raise AssertionError("curve order mismatch")
    if curve.mul(n, generator) is not None:
        raise AssertionError("generator order mismatch")
    if pow(beta, 3, p) != 1 or beta == 1:
        raise AssertionError("beta is not a primitive cubic root")
    if (lam * lam + lam + 1) % n:
        raise AssertionError("lambda is not a primitive cubic root")
    if curve.mul(lam, generator, n) != (beta * generator[0] % p, generator[1]):
        raise AssertionError("GLV action mismatch")


def curve_rows(row: tuple[int, int, tuple[int, int], int, int]) -> tuple[list[StateRow], dict[str, int]]:
    verify_fixture(row)
    p, n, generator, beta, lam = row
    curve = Curve(p)
    rows: list[StateRow] = []
    for k in range(1, n):
        point = curve.mul(k, generator, n)
        if point is None:
            raise AssertionError("identity in nonzero scalar chart")
        (ua, va), (ub, vb), _ = torsion_lift_basis(curve, n, point)
        x, y = point
        inverse_2y = pow(2 * y, -1, p)
        omega_a = ua * inverse_2y % p
        omega_b = ub * inverse_2y % p
        det_ab = (ua * vb - ub * va) % p
        position_a = (x * va - y * ua) % p
        cm_t = x**3 % p
        cm_r = x * ua % p
        cm_s = x * x % p * va % p * pow(y, -1, p) % p
        if (2 * (cm_t + 7) * cm_s - cm_t * (3 * cm_r + 1)) % p:
            raise AssertionError("CM tangent quotient relation failed")
        rows.append(StateRow(
            k, point, ua, va, ub, vb, omega_a, omega_b,
            det_ab, position_a, cm_t, cm_r, cm_s,
        ))
    anchor = rows[0]
    anchor_values = {
        "ua": anchor.ua,
        "va": anchor.va,
        "ub": anchor.ub,
        "vb": anchor.vb,
        "omega_a": anchor.omega_a,
        "omega_b": anchor.omega_b,
        "det_ab": anchor.det_ab,
        "position_a": anchor.position_a,
    }
    if any(value == 0 for value in anchor_values.values()):
        raise AssertionError("zero anchor in charged-state chart")
    return rows, {
        "p": p, "n": n, "xG": generator[0], "yG": generator[1],
        "beta": beta, "beta2": beta * beta % p, "lambda": lam,
        **{name + "G": value for name, value in anchor_values.items()},
    }


def normalized(value: int, anchor: int, p: int) -> int:
    return value * pow(anchor, -1, p) % p


def charged_columns(rows: list[StateRow], context: dict[str, int]) -> dict[str, list[int]]:
    p = context["p"]
    out = {
        "U": [normalized(row.ua, context["uaG"], p) for row in rows],
        "V": [normalized(row.va, context["vaG"], p) for row in rows],
        "OA": [normalized(row.omega_a, context["omega_aG"], p) for row in rows],
        "OB": [normalized(row.omega_b, context["omega_bG"], p) for row in rows],
        "D": [normalized(row.det_ab, context["det_abG"], p) for row in rows],
        "P": [normalized(row.position_a, context["position_aG"], p) for row in rows],
        "R": [row.cm_r for row in rows],
        "S": [row.cm_s for row in rows],
        "T": [row.cm_t for row in rows],
    }
    out["UV"] = [u * v % p for u, v in zip(out["U"], out["V"])]
    out["V3"] = [pow(v, 3, p) for v in out["V"]]
    out["U3"] = [pow(u, 3, p) for u in out["U"]]
    out["U2V"] = [u * u % p * v % p for u, v in zip(out["U"], out["V"])]
    return out


def mixed_parity_collisions(values: list[int], rows: list[StateRow]) -> int:
    seen: dict[int, int] = {}
    mixed: set[int] = set()
    for value, row in zip(values, rows):
        parity = row.k & 1
        old = seen.get(value)
        if old is not None and old != parity:
            mixed.add(value)
        else:
            seen[value] = parity
    return len(mixed)


class XorBasis:
    def __init__(self) -> None:
        self.rows: dict[int, int] = {}

    def add(self, vector: int) -> None:
        value = vector
        while value:
            pivot = value.bit_length() - 1
            if pivot in self.rows:
                value ^= self.rows[pivot]
            else:
                self.rows[pivot] = value
                return

    def contains(self, vector: int) -> bool:
        value = vector
        while value:
            pivot = value.bit_length() - 1
            if pivot not in self.rows:
                return False
            value ^= self.rows[pivot]
        return True

    @property
    def rank(self) -> int:
        return len(self.rows)


def bit_vector(signs: list[int]) -> int:
    base = signs[0]
    value = 0
    for index, sign in enumerate(signs[1:]):
        if sign != base:
            value |= 1 << index
    return value


def structural_constants(context: dict[str, int]) -> dict[str, int]:
    p = context["p"]
    raw = {
        "zero": 0,
        "one": 1,
        "minus_one": -1,
        "seven": 7,
        "minus_seven": -7,
        "xG": context["xG"],
        "minus_xG": -context["xG"],
        "yG": context["yG"],
        "minus_yG": -context["yG"],
        "beta": context["beta"],
        "beta2": context["beta2"],
        "lambda": context["lambda"],
        "n": context["n"],
        "half": (context["n"] - 1) // 2,
        "inv2": pow(2, -1, p),
        "inv3": pow(3, -1, p),
        "uaG": context["uaG"],
        "vaG": context["vaG"],
        "omega_aG": context["omega_aG"],
        "omega_bG": context["omega_bG"],
        "det_abG": context["det_abG"],
    }
    return {name: value % p for name, value in raw.items()}
