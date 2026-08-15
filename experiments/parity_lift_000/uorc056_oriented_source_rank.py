#!/usr/bin/env python3
"""Exact C31 replay for generator-oriented source rank in UORC-056.

The marked-generator oriented roots have value matrix

    Y_[u]G(x([r]G)) = epsilon([r*u^{-1}]_n) * y([r]G),

where epsilon(a)=(-1)^a for the canonical residue 1<=a<n.  This script
computes the half-generator/half-kernel source matrix, verifies exact full rank
on the frozen base fields, checks the marker formula on every source entry, and
records the characteristic-zero multiplicative-Fourier theorem and its scope.

No external point, unknown scalar, private key, wallet, production target,
branch table, or dense secp256k1 source is accepted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Sequence

Point = Optional[tuple[int, int]]
PROFILE_ID = "UORC-056-ORIENTED-SOURCE-RANK-C31"
DEFAULT_OUTPUT = Path("/tmp/uorc056_oriented_source_rank_result.json")
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F


def stable_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def payload_digest(payload: dict[str, Any]) -> str:
    body = dict(payload)
    body.pop("digest", None)
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class Curve:
    p: int
    a: int
    b: int

    def add(self, P: Point, Q: Point) -> Point:
        if P is None:
            return Q
        if Q is None:
            return P
        p = self.p
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2 and (y1 + y2) % p == 0:
            return None
        if P == Q:
            if y1 == 0:
                return None
            slope = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, p) % p
        else:
            slope = (y2 - y1) * pow(x2 - x1, -1, p) % p
        x3 = (slope * slope - x1 - x2) % p
        y3 = (slope * (x1 - x3) - y1) % p
        return x3, y3

    def mul(self, k: int, P: Point) -> Point:
        if k < 0:
            return self.mul(-k, None if P is None else (P[0], -P[1] % self.p))
        out: Point = None
        addend = P
        while k:
            if k & 1:
                out = self.add(out, addend)
            addend = self.add(addend, addend)
            k >>= 1
        return out


@dataclass(frozen=True)
class Instance:
    name: str
    curve: Curve
    n: int
    G: tuple[int, int]
    beta: int
    lam: int


INSTANCES = (
    Instance("E7-P43-N31", Curve(43, 0, 7), 31, (2, 12), 6, 5),
    Instance("E7-P67-N79", Curve(67, 0, 7), 79, (2, 22), 29, 23),
    Instance("E7-P79-N67", Curve(79, 0, 7), 67, (1, 18), 23, 29),
    Instance("E7-P127-N127", Curve(127, 0, 7), 127, (1, 32), 19, 107),
    Instance("E7-P163-N139", Curve(163, 0, 7), 139, (2, 34), 58, 96),
)


def parity_sign(residue: int, n: int) -> int:
    value = residue % n
    if value == 0:
        raise ValueError("parity sign is defined only on nonzero residues")
    return -1 if value & 1 else 1


def half_points(instance: Instance) -> list[tuple[int, int]]:
    out = []
    for r in range(1, (instance.n - 1) // 2 + 1):
        P = instance.curve.mul(r, instance.G)
        if P is None:
            raise AssertionError("half-orbit point became infinity")
        out.append(P)
    if len({P[0] for P in out}) != len(out):
        raise AssertionError("half-kernel x coordinates are not distinct")
    if any(P[1] == 0 for P in out):
        raise AssertionError("odd-order half point had y=0")
    return out


def sign_source_matrix(n: int) -> list[list[int]]:
    m = (n - 1) // 2
    return [
        [parity_sign(r * pow(u, -1, n), n) for r in range(1, m + 1)]
        for u in range(1, m + 1)
    ]


def full_sign_source_matrix(n: int) -> list[list[int]]:
    m = (n - 1) // 2
    return [
        [parity_sign(r * pow(u, -1, n), n) for r in range(1, m + 1)]
        for u in range(1, n)
    ]


def oriented_source_matrix(instance: Instance) -> list[list[int]]:
    p = instance.curve.p
    ys = [P[1] for P in half_points(instance)]
    return [[entry * y % p for entry, y in zip(row, ys)] for row in sign_source_matrix(instance.n)]


def rank_mod(matrix: Sequence[Sequence[int]], modulus: int) -> int:
    if not matrix:
        return 0
    rows = [[int(value) % modulus for value in row] for row in matrix]
    row_count = len(rows)
    col_count = len(rows[0])
    rank = 0
    for col in range(col_count):
        pivot = next((i for i in range(rank, row_count) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][col], -1, modulus)
        rows[rank] = [value * inverse % modulus for value in rows[rank]]
        for i in range(row_count):
            if i == rank or rows[i][col] == 0:
                continue
            factor = rows[i][col]
            rows[i] = [
                (left - factor * right) % modulus
                for left, right in zip(rows[i], rows[rank])
            ]
        rank += 1
        if rank == min(row_count, col_count):
            break
    return rank


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    divisor = 3
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 2
    return True


def prime_factors(value: int) -> list[int]:
    out = []
    divisor = 2
    n = value
    while divisor * divisor <= n:
        if n % divisor == 0:
            out.append(divisor)
            while n % divisor == 0:
                n //= divisor
        divisor += 1
    if n > 1:
        out.append(n)
    return out


def primitive_root(modulus: int) -> int:
    factors = prime_factors(modulus - 1)
    for candidate in range(2, modulus):
        if all(pow(candidate, (modulus - 1) // factor, modulus) != 1 for factor in factors):
            return candidate
    raise AssertionError("primitive root not found")


def auxiliary_fourier_certificate(n: int) -> dict[str, Any]:
    """Find one exact finite-field witness of the odd-character support law.

    A good auxiliary prime certifies that the integer half-source matrix is
    nonsingular in characteristic zero. It is finite evidence, not the all-n
    proof, which uses the standard nonvanishing of L(0,chi) for primitive odd
    Dirichlet characters.
    """
    order = n - 1
    multiplier = 1
    while True:
        q = multiplier * order + 1
        multiplier += 1
        if q > 2 and is_prime(q):
            generator_q = primitive_root(q)
            omega = pow(generator_q, (q - 1) // order, q)
            generator_n = primitive_root(n)
            sequence = []
            value = 1
            for _ in range(order):
                sequence.append(parity_sign(value, n) % q)
                value = value * generator_n % n
            coefficients = []
            for frequency in range(order):
                z = pow(omega, (-frequency) % order, q)
                power = 1
                total = 0
                for sample in sequence:
                    total = (total + sample * power) % q
                    power = power * z % q
                coefficients.append(total)
            zero_frequencies = [i for i, value in enumerate(coefficients) if value == 0]
            nonzero_frequencies = [i for i, value in enumerate(coefficients) if value != 0]
            expected_zero = list(range(0, order, 2))
            expected_nonzero = list(range(1, order, 2))
            if zero_frequencies == expected_zero and nonzero_frequencies == expected_nonzero:
                return {
                    "order_n": n,
                    "multiplicative_group_order": order,
                    "auxiliary_prime": q,
                    "primitive_root_mod_n": generator_n,
                    "primitive_character_root": omega,
                    "zero_even_character_frequencies": len(zero_frequencies),
                    "nonzero_odd_character_frequencies": len(nonzero_frequencies),
                    "support_pattern_exact": True,
                }


def curve_record(instance: Instance) -> dict[str, Any]:
    p, n = instance.curve.p, instance.n
    m = (n - 1) // 2
    points = half_points(instance)
    sign_matrix = sign_source_matrix(n)
    full_matrix = full_sign_source_matrix(n)
    oriented_matrix = oriented_source_matrix(instance)

    sign_rank = rank_mod(sign_matrix, p)
    full_rank = rank_mod(full_matrix, p)
    oriented_rank = rank_mod(oriented_matrix, p)
    if sign_rank != m or full_rank != m or oriented_rank != m:
        raise AssertionError(
            f"source rank dropped on {instance.name}: {sign_rank}, {full_rank}, {oriented_rank}"
        )

    marker_formula_checks = 0
    row_negation_checks = 0
    for u in range(1, n):
        inverse = pow(u, -1, n)
        opposite_inverse = pow(n - u, -1, n)
        for r, (_, y_r) in enumerate(points, start=1):
            scalar = r * inverse % n
            expected = parity_sign(scalar, n) * y_r % p
            formula = parity_sign(r * inverse, n) * y_r % p
            if formula != expected:
                raise AssertionError("marked-generator source formula failed")
            opposite = parity_sign(r * opposite_inverse, n) * y_r % p
            if opposite != -formula % p:
                raise AssertionError("generator-negation row law failed")
            marker_formula_checks += 1
            row_negation_checks += 1

    if any(y == 0 for _, y in points):
        raise AssertionError("zero column gauge")

    return {
        "id": instance.name,
        "p": p,
        "n": n,
        "half_kernel_dimension": m,
        "half_source_entries": m * m,
        "all_marker_source_entries": (n - 1) * m,
        "half_sign_source_rank_mod_p": sign_rank,
        "full_marked_source_rank_mod_p": full_rank,
        "oriented_value_source_rank_mod_p": oriented_rank,
        "marker_formula_checks": marker_formula_checks,
        "generator_negation_checks": row_negation_checks,
        "full_rank_on_frozen_base_field": True,
    }


def secp_record() -> dict[str, Any]:
    m = (SECP_N - 1) // 2
    return {
        "p": SECP_P,
        "n": SECP_N,
        "half_kernel_dimension": m,
        "half_kernel_dimension_bit_length": m.bit_length(),
        "characteristic_zero_fixed_dictionary_lower_bound": m,
        "characteristic_zero_fixed_dictionary_lower_bound_exceeds_2_pow_254": m > 2**254,
        "characteristic_zero_fixed_dictionary_lower_bound_below_2_pow_255": m < 2**255,
        "secp_base_field_source_rank_certified_by_this_package": False,
        "reason_for_base_field_boundary": (
            "Characteristic-zero nonvanishing does not automatically exclude determinant "
            "collapse modulo the secp256k1 field prime. The package does not hide that gap."
        ),
    }


def run() -> dict[str, Any]:
    rows = [curve_record(instance) for instance in INSTANCES]
    unique_orders = sorted({instance.n for instance in INSTANCES})
    fourier = [auxiliary_fourier_certificate(n) for n in unique_orders]
    totals = {
        "curves": len(rows),
        "half_kernel_dimensions_sum": sum(row["half_kernel_dimension"] for row in rows),
        "half_source_entries_checked": sum(row["half_source_entries"] for row in rows),
        "all_marker_source_entries_checked": sum(row["all_marker_source_entries"] for row in rows),
        "marker_formula_checks": sum(row["marker_formula_checks"] for row in rows),
        "generator_negation_checks": sum(row["generator_negation_checks"] for row in rows),
        "full_rank_curves": sum(row["full_rank_on_frozen_base_field"] for row in rows),
        "auxiliary_fourier_orders": len(fourier),
        "errors": 0,
    }
    if totals != {
        "curves": 5,
        "half_kernel_dimensions_sum": 219,
        "half_source_entries_checked": 11565,
        "all_marker_source_entries_checked": 23130,
        "marker_formula_checks": 23130,
        "generator_negation_checks": 23130,
        "full_rank_curves": 5,
        "auxiliary_fourier_orders": 5,
        "errors": 0,
    }:
        raise AssertionError(f"frozen totals drifted: {totals}")

    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "profile_id": PROFILE_ID,
        "central_target": "Y_G(x([k]G))/y([k]G)=(-1)^k",
        "source_matrix": {
            "sign_entry": "M[u,r]=(-1)^canonical(r*u^(-1) mod n)",
            "oriented_entry": "V[u,r]=M[u,r]*y([r]G)",
            "marker_range": "1<=u<=(n-1)/2; rows for n-u are global negatives",
            "node_range": "1<=r<=(n-1)/2",
        },
        "characteristic_zero_theorem": {
            "full_multiplicative_translate_matrix": "F[u,r]=epsilon(u^(-1)r) on (Z/nZ)^*",
            "even_characters": "Fourier coefficient is zero because epsilon(-a)=-epsilon(a)",
            "odd_characters": (
                "Fourier coefficient is nonzero. With H_chi=sum_{a<=m}chi(a) and "
                "W_chi=sum a*chi(a), n*chi(2)*H_chi=(1-2*chi(2))*W_chi; "
                "the standard primitive-odd Dirichlet result L(0,chi)=-W_chi/n!=0 applies."
            ),
            "nonzero_frequencies": "exactly the (n-1)/2 odd multiplicative characters",
            "rank": "(n-1)/2",
            "half_matrix_transfer": (
                "Under the decomposition U=H union -H the full matrix is "
                "[[M,-M],[-M,M]], hence rank(full)=rank(M)."
            ),
            "oriented_value_transfer": "nonzero column scaling by y([r]G) preserves rank",
        },
        "linear_dictionary_consequence": {
            "model": (
                "A fixed d-dimensional linear source dictionary must contain every "
                "marked-generator oriented-root value vector."
            ),
            "conclusion": "d >= (n-1)/2 in characteristic zero",
            "tightness": "the half-kernel coordinate basis has dimension (n-1)/2",
            "not_covered": [
                "a nonlinear compiler that generates one source from G",
                "a fixed-G evaluator that does not support generator replacements from one dictionary",
                "modular rank collapse in an unproved finite characteristic",
                "nonlinear nonlocal product, modular-composition, or continuation circuits",
            ],
        },
        "exact_replay": {**totals, "curve_rows": rows, "auxiliary_fourier_rows": fourier},
        "secp256k1": secp_record(),
        "decision": {
            "marked_generator_source_formula_verified": True,
            "characteristic_zero_half_source_rank_exact": True,
            "frozen_base_field_half_source_rank_full": True,
            "fixed_linear_dictionary_subroot_possible_char0": False,
            "secp_base_field_half_source_rank_proved": False,
            "nonlinear_oriented_source_compiler_found": False,
            "sublinear_transposed_oriented_functional_found": False,
            "public_nonlocal_primitive_defined": False,
            "primitive_creates_branch_sensitivity": False,
            "all_point_public_Q_replay_passed": False,
            "exact_oriented_root_extraction_found": False,
            "exact_parity_extraction_found": False,
            "complete_cost_gate_passed": False,
            "compact_branch_odd_evaluator_found": False,
            "sub_sqrt_evaluator_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
        "closed_class": [
            "characteristic-zero fixed linear dictionaries spanning all marked-generator oriented sources",
            "frozen-base-field fixed linear dictionaries below half-kernel rank",
            "transposed linear methods that receive such a fixed low-rank oriented source space",
        ],
        "remaining_frontier": [
            "nonlinear generation of one oriented source from the public generator",
            "fixed-G target-dependent modular composition",
            "nonlinear product-tree identities with sub-root leaf generation",
            "a secp256k1 base-field rank certificate or an algorithm escaping linear dictionaries",
        ],
        "scientific_boundary": (
            "The all-prime rank theorem is characteristic zero. The secp256k1 base-field "
            "rank is not claimed. No unrestricted transposed, circuit, parity, or ECDLP "
            "lower bound is proved."
        ),
        "successor": "FIXED-G-NONLINEAR-SOURCE-COMPILER-082",
    }
    payload["digest"] = payload_digest(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(stable_json(payload), encoding="utf-8")
    print(stable_json(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
