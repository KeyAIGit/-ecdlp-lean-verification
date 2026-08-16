#!/usr/bin/env python3
"""Exact structural GLV-DFT character and quartic-overfit screens for C43."""
from __future__ import annotations

import hashlib
import json
from typing import Any

from uorc056_c39_half_miller import TOYS, half_sequence
from uorc056_c43_local_glv_branch import HELD_OUT, carry_sign

TARGETS = ("parity", "carry_g", "sector_J")
QUARTIC_PRIMES = {229, 997, 2137}


def bit_vector(signs: list[int]) -> int:
    base = signs[0]
    vector = 0
    for index, sign in enumerate(signs[1:]):
        if sign != base:
            vector |= 1 << index
    return vector


def target_values(index: int, order: int, eigenvalue: int) -> dict[str, int]:
    parity = 1 if index % 2 == 0 else -1
    carry = carry_sign(index, order, eigenvalue)
    return {
        "parity": parity,
        "carry_g": carry,
        "sector_J": parity * carry,
    }


def character_table(prime: int) -> list[int]:
    table = [0] * prime
    for value in range(1, prime):
        table[value] = (
            1 if pow(value, (prime - 1) // 2, prime) == 1 else -1
        )
    return table


def dft_records(row):
    curve, order, generator, shift, beta, lam, half, values = half_sequence(row)
    beta_field = curve.c(beta)
    one = curve.c(1)
    records = []
    for index in range(1, order):
        orbit = [
            index,
            (lam * index) % order,
            (lam * lam * index) % order,
        ]
        forward = [values[position] for position in orbit]
        reverse = [values[order - position] for position in orbit]
        dft = [
            forward[0] + forward[1] + forward[2],
            forward[0] + beta_field ** 2 * forward[1] + beta_field * forward[2],
            forward[0] + beta_field * forward[1] + beta_field ** 2 * forward[2],
        ]
        reverse_dft = [
            reverse[0] + reverse[1] + reverse[2],
            reverse[0] + beta_field ** 2 * reverse[1] + beta_field * reverse[2],
            reverse[0] + beta_field * reverse[1] + beta_field ** 2 * reverse[2],
        ]
        expressions = {
            "f0": forward[0],
            "f1": forward[1],
            "f2": forward[2],
            "L0": dft[0],
            "L1": dft[1],
            "L2": dft[2],
            "Ln0": reverse_dft[0],
            "Ln1": reverse_dft[1],
            "Ln2": reverse_dft[2],
            "L1L2": dft[1] * dft[2],
            "L1_over_L2": dft[1] / dft[2] if dft[2] else one * 0,
            "L0L1L2": dft[0] * dft[1] * dft[2],
            "cyclic_product": forward[0] * forward[1] * forward[2],
            "cyclic_alt": (
                forward[0] * forward[1].conj() * forward[2]
                - forward[0].conj() * forward[1] * forward[2].conj()
            ),
            "wedge_sum": (
                forward[0] * forward[1].conj()
                - forward[1] * forward[0].conj()
                + forward[1] * forward[2].conj()
                - forward[2] * forward[1].conj()
                + forward[2] * forward[0].conj()
                - forward[0] * forward[2].conj()
            ),
            "L_wedge": dft[1] * dft[2].conj() - dft[2] * dft[1].conj(),
            "L_dot": dft[1] * dft[2].conj() + dft[2] * dft[1].conj(),
        }
        for left in range(3):
            for right in range(left, 3):
                expressions[f"L{left}L{right}"] = dft[left] * dft[right]
            for right in range(left + 1, 3):
                expressions[f"Lminor{left}{right}"] = (
                    dft[left] * dft[right].conj()
                    - dft[right] * dft[left].conj()
                )
        records.append((target_values(index, order, lam), expressions))
    return curve, order, generator, shift, beta, lam, half, records


def structural_coefficients(
    curve, order, generator, shift, beta, lam, half, records
) -> list[int]:
    prime = curve.p
    values = {
        0,
        1,
        -1,
        beta,
        beta * beta,
        curve.d,
        generator[0].a,
        generator[1].a,
        shift[0].a,
        shift[0].b,
        shift[1].a,
        shift[1].b,
        lam % prime,
        half % prime,
        (prime - 1) // 2,
    }
    for expression in records[0][1].values():
        values.add(expression.a)
        values.add(expression.b)
        if expression.b:
            inverse = pow(expression.b, -1, prime)
            values.add((-expression.a * inverse) % prime)
            values.add((expression.a * inverse) % prime)
        if expression.a:
            inverse = pow(expression.a, -1, prime)
            values.add((-expression.b * inverse) % prime)
            values.add((expression.b * inverse) % prime)
    closed = {value % prime for value in values}
    for value in list(closed):
        closed.add((-value) % prime)
        closed.add((value * value) % prime)
        if value:
            closed.add(pow(value, -1, prime))
    return sorted(closed)


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


def valid_atom_vector(
    records,
    expression_name: str,
    coefficient: int | None,
    table: list[int],
    prime: int,
) -> int | None:
    signs = []
    for targets, expressions in records:
        value = expressions[expression_name]
        argument = (
            value.b if coefficient is None
            else (value.a + coefficient * value.b) % prime
        )
        sign = table[argument]
        if sign == 0:
            return None
        signs.append(sign)
    return bit_vector(signs)


def line_atoms(values, table: list[int], prime: int) -> dict[int | str, int]:
    atoms: dict[int | str, int] = {}
    for coefficient in range(prime):
        signs = []
        valid = True
        for value in values:
            sign = table[(value.a + coefficient * value.b) % prime]
            if sign == 0:
                valid = False
                break
            signs.append(sign)
        if valid:
            atoms[coefficient] = bit_vector(signs)
    signs = [table[value.b] for value in values]
    if all(signs):
        atoms["inf"] = bit_vector(signs)
    return atoms


def pair_map(atoms: dict[int | str, int]) -> dict[int, tuple[int | str, int | str]]:
    items = list(atoms.items())
    pairs: dict[int, tuple[int | str, int | str]] = {}
    for left in range(len(items)):
        left_name, left_vector = items[left]
        for right in range(left + 1, len(items)):
            right_name, right_vector = items[right]
            pairs.setdefault(left_vector ^ right_vector, (left_name, right_name))
    return pairs


def quartic_two_plus_two(records, table, prime, targets):
    f0_values = [expressions["f0"] for _, expressions in records]
    l0_values = [expressions["L0"] for _, expressions in records]
    f0_atoms = line_atoms(f0_values, table, prime)
    l0_atoms = line_atoms(l0_values, table, prime)
    f0_pairs = pair_map(f0_atoms)
    l0_pairs = pair_map(l0_atoms)
    solutions = {}
    for target_name, target_vector in targets.items():
        solution = None
        for vector, l0_pair in l0_pairs.items():
            f0_pair = f0_pairs.get(target_vector ^ vector)
            if f0_pair is not None:
                solution = {"L0": list(l0_pair), "f0": list(f0_pair)}
                break
        solutions[target_name] = solution
    return {
        "f0_valid_lines": len(f0_atoms),
        "L0_valid_lines": len(l0_atoms),
        "f0_pair_syndromes": len(f0_pairs),
        "L0_pair_syndromes": len(l0_pairs),
        "solutions": solutions,
    }


def analyze_curve(row, label: str) -> dict[str, Any]:
    curve, order, generator, shift, beta, lam, half, records = dft_records(row)
    prime = curve.p
    table = character_table(prime)
    names = sorted(records[0][1])
    coefficients = structural_coefficients(
        curve, order, generator, shift, beta, lam, half, records
    )
    basis = XorBasis()
    declared_atoms = 0
    valid_atoms = 0
    for expression_name in names:
        for coefficient in coefficients:
            declared_atoms += 1
            vector = valid_atom_vector(
                records, expression_name, coefficient, table, prime
            )
            if vector is not None:
                valid_atoms += 1
                basis.add(vector)
        declared_atoms += 1
        vector = valid_atom_vector(records, expression_name, None, table, prime)
        if vector is not None:
            valid_atoms += 1
            basis.add(vector)

    target_vectors = {
        target: bit_vector([values[target] for values, _ in records])
        for target in TARGETS
    }
    target_span = {
        target: basis.contains(vector)
        for target, vector in target_vectors.items()
    }
    quartic = (
        quartic_two_plus_two(records, table, prime, target_vectors)
        if prime in QUARTIC_PRIMES
        else None
    )
    return {
        "label": label,
        "p": prime,
        "n": order,
        "expressions": len(names),
        "structural_coefficients": len(coefficients),
        "declared_character_atoms": declared_atoms,
        "valid_character_atoms": valid_atoms,
        "character_span_rank": basis.rank,
        "targets_in_arbitrary_product_span": target_span,
        "quartic_two_L0_two_f0": quartic,
        "errors": 0,
    }


def build_dft_payload() -> dict[str, Any]:
    rows = [
        analyze_curve(row, f"frozen-{index + 1}")
        for index, row in enumerate(TOYS)
    ] + [
        analyze_curve(row, f"heldout-{index + 1}")
        for index, row in enumerate(HELD_OUT)
    ]
    decisive = next(row for row in rows if row["p"] == 2137)
    quartic_profile = {
        str(row["p"]): row["quartic_two_L0_two_f0"]
        for row in rows
        if row["quartic_two_L0_two_f0"] is not None
    }
    payload: dict[str, Any] = {
        "profile_id": "UORC-056-C43-GLV-DFT-STRUCTURAL-CHARACTERS",
        "schema_version": "1.0",
        "grammar": {
            "states": (
                "27 fixed Fp2 expressions from f(Q), f(phi Q), f(phi^2 Q), "
                "their C3 DFT, products, ratios and Frobenius wedges"
            ),
            "atoms": "chi_p(Re(E)+b Im(E)) and chi_p(Im(E))",
            "coefficient_set": (
                "public structural constants, anchor slopes, and closure under "
                "negation, inversion and squaring"
            ),
            "combiner": "arbitrary product of every everywhere-nonzero atom",
        },
        "curves": rows,
        "quartic_overfit_profile": quartic_profile,
        "aggregate": {
            "curves": len(rows),
            "frozen": len(TOYS),
            "heldout": len(HELD_OUT),
            "declared_character_atoms": sum(
                int(row["declared_character_atoms"]) for row in rows
            ),
            "valid_character_atoms": sum(
                int(row["valid_character_atoms"]) for row in rows
            ),
            "decisive_p2137_all_targets_absent": not any(
                bool(value)
                for value in decisive["targets_in_arbitrary_product_span"].values()
            ),
            "quartic_fits_p229": all(
                value is not None
                for value in quartic_profile["229"]["solutions"].values()
            ),
            "quartic_fits_p997": all(
                value is not None
                for value in quartic_profile["997"]["solutions"].values()
            ),
            "quartic_fails_p2137": all(
                value is None
                for value in quartic_profile["2137"]["solutions"].values()
            ),
            "errors": sum(int(row["errors"]) for row in rows),
        },
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["digest"] = hashlib.sha256(raw).hexdigest()
    return payload
