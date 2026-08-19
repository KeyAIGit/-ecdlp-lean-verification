#!/usr/bin/env python3
"""Shared feature and GF(2) primitives for the C52 replay."""
from __future__ import annotations

from typing import Any

FEATURE_NAMES = (
    "ua", "va", "ub", "vb", "omega_a", "omega_b", "det_ab",
    "ua_anchor_ratio", "va_anchor_ratio", "omega_a_anchor_ratio",
    "omega_b_anchor_ratio", "vb_anchor_ratio", "wedge_u", "wedge_v",
    "wedge_aa", "wedge_bb", "wedge_ab", "wedge_ba",
    "position_a", "position_b", "cm_R", "cm_S",
)
PAIR_FEATURES = (
    ("omega_a_anchor_ratio", "omega_b_anchor_ratio"),
    ("ua_anchor_ratio", "va_anchor_ratio"),
    ("va_anchor_ratio", "vb_anchor_ratio"),
    ("cm_R", "cm_S"),
    ("omega_a", "omega_b"),
    ("ua", "va"),
    ("det_ab", "omega_b_anchor_ratio"),
)
COEFFICIENT_NAMES = (
    "zero", "one", "minus_one", "b", "minus_b", "xG", "minus_xG",
    "yG", "minus_yG", "beta", "beta2", "lambda", "half", "n_mod_p",
    "inv2", "inv3", "inv6b", "uaG", "vaG", "omegaAG", "omegaBG", "detG",
)


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
    vector = 0
    for index, sign in enumerate(signs[1:]):
        if sign != base:
            vector |= 1 << index
    return vector


def mixed_parity_collisions(values: list[int], parities: list[int]) -> int:
    seen: dict[int, int] = {}
    mixed: set[int] = set()
    for value, parity in zip(values, parities):
        old = seen.get(value)
        if old is not None and old != parity:
            mixed.add(value)
        else:
            seen[value] = parity
    return len(mixed)


def tuple_mixed(values: list[tuple[int, ...]], parities: list[int]) -> bool:
    seen: dict[tuple[int, ...], int] = {}
    for value, parity in zip(values, parities):
        if value in seen and seen[value] != parity:
            return True
        seen[value] = parity
    return False


def build_feature_row(
    p: int,
    point: tuple[int, int],
    tangent_a: tuple[int, int],
    tangent_b: tuple[int, int],
    anchor: dict[str, int],
) -> dict[str, int]:
    x, y = point
    ua, va = tangent_a
    ub, vb = tangent_b
    inverse = lambda value: pow(value, -1, p)
    omega_a = ua * inverse(2 * y) % p
    omega_b = ub * inverse(2 * y) % p
    det_ab = (ua * vb - ub * va) % p
    return {
        "ua": ua,
        "va": va,
        "ub": ub,
        "vb": vb,
        "omega_a": omega_a,
        "omega_b": omega_b,
        "det_ab": det_ab,
        "ua_anchor_ratio": ua * inverse(anchor["uaG"]) % p,
        "va_anchor_ratio": va * inverse(anchor["vaG"]) % p,
        "omega_a_anchor_ratio": omega_a * inverse(anchor["omegaAG"]) % p,
        "omega_b_anchor_ratio": omega_b * inverse(anchor["omegaBG"]) % p,
        "vb_anchor_ratio": vb * inverse(anchor["vbG"]) % p,
        "wedge_u": (ua * anchor["ubG"] - ub * anchor["uaG"]) % p,
        "wedge_v": (va * anchor["vbG"] - vb * anchor["vaG"]) % p,
        "wedge_aa": (ua * anchor["vaG"] - va * anchor["uaG"]) % p,
        "wedge_bb": (ub * anchor["vbG"] - vb * anchor["ubG"]) % p,
        "wedge_ab": (ua * anchor["vbG"] - vb * anchor["uaG"]) % p,
        "wedge_ba": (ub * anchor["vaG"] - va * anchor["ubG"]) % p,
        "position_a": (x * va - y * ua) % p,
        "position_b": (x * vb - y * ub) % p,
        "cm_R": x * ua % p,
        "cm_S": x * x % p * va % p * inverse(y) % p,
    }


def coefficient_values(context: dict[str, int]) -> dict[str, int]:
    p = context["p"]
    b = context["b"]
    raw = {
        "zero": 0,
        "one": 1,
        "minus_one": -1,
        "b": b,
        "minus_b": -b,
        "xG": context["xG"],
        "minus_xG": -context["xG"],
        "yG": context["yG"],
        "minus_yG": -context["yG"],
        "beta": context["beta"],
        "beta2": context["beta"] ** 2,
        "lambda": context["lambda"],
        "half": (context["n"] - 1) // 2,
        "n_mod_p": context["n"],
        "inv2": pow(2, -1, p),
        "inv3": pow(3, -1, p),
        "inv6b": pow(6 * b, -1, p),
        "uaG": context["uaG"],
        "vaG": context["vaG"],
        "omegaAG": context["omegaAG"],
        "omegaBG": context["omegaBG"],
        "detG": context["detG"],
    }
    return {name: value % p for name, value in raw.items()}
