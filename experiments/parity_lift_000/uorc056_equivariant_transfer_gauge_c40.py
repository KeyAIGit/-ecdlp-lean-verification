#!/usr/bin/env python3
"""Exact frozen replay for UORC-056 C40 equivariant transfer gauge.

The script uses only inherited public toy curves and known scalars. It never
accepts an external point, wallet, key, or production target.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from uorc056_regularized_anchor_miller_c36 import (
    INSTANCES,
    SECP_N,
    Curve,
    base_point,
    least_nonsquare,
    miller,
    trace_zero_twist_point,
)

GLV_LAMBDA = {
    "E7-P43-N31": 5,
    "E7-P67-N79": 23,
    "E7-P79-N67": 29,
    "E7-P127-N127": 107,
    "E7-P163-N139": 96,
}


def fp2_key(value: Any) -> tuple[int, int]:
    for names in (("a", "b"), ("real", "imag"), ("x", "y"), ("c0", "c1")):
        if all(hasattr(value, name) for name in names):
            return (
                int(getattr(value, names[0])) % int(value.p),
                int(getattr(value, names[1])) % int(value.p),
            )
    integers = [int(item) for item in vars(value).values() if isinstance(item, int)]
    return integers[0] % int(value.p), integers[1] % int(value.p)


def shifted(curve: Curve, index: int, source: Any, query: Any, shift: Any) -> Any:
    return miller(curve, index, source, curve.add(shift, query)) / miller(
        curve, index, source, shift
    )


def norm_one(curve: Curve, index: int, source: Any, query: Any, shift: Any) -> Any:
    return shifted(curve, index, source, query, shift) / shifted(
        curve, index, source, query, curve.neg(shift)
    )


def inversion_state(curve: Curve, index: int, source: Any, query: Any, shift: Any) -> Any:
    return norm_one(curve, index, source, query, shift) * norm_one(
        curve, index, curve.neg(source), query, shift
    )


def trim(poly: list[int], p: int) -> list[int]:
    out = [value % p for value in poly]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def add(left: list[int], right: list[int], p: int) -> list[int]:
    out = [0] * max(len(left), len(right))
    for index in range(len(out)):
        out[index] = (
            (left[index] if index < len(left) else 0)
            + (right[index] if index < len(right) else 0)
        ) % p
    return trim(out, p)


def sub(left: list[int], right: list[int], p: int) -> list[int]:
    return add(left, [(-value) % p for value in right], p)


def mul(left: list[int], right: list[int], p: int) -> list[int]:
    out = [0] * (len(left) + len(right) - 1)
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            out[i + j] = (out[i + j] + x * y) % p
    return trim(out, p)


def scale(poly: list[int], scalar: int, p: int) -> list[int]:
    return trim([scalar * value % p for value in poly], p)


def evaluate(poly: list[int], value: int, p: int) -> int:
    out = 0
    for coefficient in reversed(poly):
        out = (out * value + coefficient) % p
    return out


def interpolate(xs: list[int], ys: list[int], p: int) -> list[int]:
    if len(set(xs)) != len(xs):
        raise AssertionError("pair coordinates are not distinct")
    out = [0]
    for index, (x, y) in enumerate(zip(xs, ys)):
        numerator = [1]
        denominator = 1
        for other_index, other in enumerate(xs):
            if index == other_index:
                continue
            numerator = mul(numerator, [(-other) % p, 1], p)
            denominator = denominator * (x - other) % p
        out = add(out, scale(numerator, y * pow(denominator, -1, p), p), p)
    return trim(out, p)


def even_representative(value: int, order: int) -> int:
    residue = value % order
    if residue == 0:
        raise ValueError("zero has no nonzero pair representative")
    return residue if residue % 2 == 0 else order - residue


def pair_cycles(representatives: list[int], multiplier: int, order: int) -> list[list[int]]:
    unseen = set(representatives)
    cycles: list[list[int]] = []
    while unseen:
        start = min(unseen)
        cycle: list[int] = []
        current = start
        while current not in cycle:
            cycle.append(current)
            unseen.discard(current)
            current = even_representative(multiplier * current, order)
        if current != start:
            raise AssertionError("permutation cycle did not return to its start")
        cycles.append(cycle)
    return cycles


def curve_replay(instance: Any) -> dict[str, object]:
    p, n = int(instance.p), int(instance.n)
    pair_count = (n - 1) // 2
    curve = Curve(p, 0, 7, least_nonsquare(p))
    generator = base_point(curve, instance.generator)
    shift = trace_zero_twist_point(curve)
    table = [curve.mul(scalar, generator) for scalar in range(n)]

    one = None
    z_values: dict[int, int] = {}
    anti_values: dict[int, int] = {}
    for scalar in range(1, n):
        state = inversion_state(curve, pair_count, generator, table[scalar], shift)
        one = state / state
        symmetric = state + one / state
        antisymmetric = state - one / state
        symmetric_real, symmetric_imag = fp2_key(symmetric)
        antisymmetric_real, antisymmetric_imag = fp2_key(antisymmetric)
        if symmetric_imag != 0 or antisymmetric_real != 0 or antisymmetric_imag == 0:
            raise AssertionError("spectral coordinate reduction failed")
        z_values[scalar] = symmetric_real
        anti_values[scalar] = antisymmetric_imag
    assert one is not None

    representatives = list(range(2, n, 2))
    if len(representatives) != pair_count:
        raise AssertionError("pair representative count mismatch")
    if len({z_values[value] for value in representatives}) != pair_count:
        raise AssertionError("pair spectral coordinates are not distinct")
    root_values = {
        value: pow(anti_values[value], -1, p)
        for value in representatives
    }

    multiplier_rows: list[dict[str, object]] = []
    for name, multiplier in (
        ("doubling", 2),
        ("glv", GLV_LAMBDA[instance.name]),
    ):
        targets = [
            even_representative(multiplier * value, n)
            for value in representatives
        ]
        coordinate_map = interpolate(
            [z_values[value] for value in representatives],
            [z_values[target] for target in targets],
            p,
        )
        transfer = interpolate(
            [z_values[value] for value in representatives],
            [
                root_values[target] * pow(root_values[value], -1, p) % p
                for value, target in zip(representatives, targets)
            ],
            p,
        )

        square_checks = 0
        for value, target in zip(representatives, targets):
            z = z_values[value]
            target_z = z_values[target]
            observed_map = evaluate(coordinate_map, z, p)
            observed_transfer = evaluate(transfer, z, p)
            if observed_map != target_z:
                raise AssertionError("coordinate transfer interpolation failed")
            expected_transfer = (
                root_values[target] * pow(root_values[value], -1, p) % p
            )
            if observed_transfer != expected_transfer:
                raise AssertionError("oriented transfer interpolation failed")
            if (
                observed_transfer * observed_transfer * (target_z * target_z - 4)
                - (z * z - 4)
            ) % p != 0:
                raise AssertionError("public square-transfer identity failed")
            square_checks += 1

        cycles = pair_cycles(representatives, multiplier, n)
        for cycle in cycles:
            product = 1
            for value in cycle:
                product = product * evaluate(
                    transfer, z_values[value], p
                ) % p
            if product != 1:
                raise AssertionError("Hilbert-90 loop product failed")

        multiplier_rows.append({
            "name": name,
            "multiplier": multiplier,
            "cycles": len(cycles),
            "cycle_lengths": sorted({len(cycle) for cycle in cycles}),
            "coordinate_map_degree": len(coordinate_map) - 1,
            "coordinate_map_support": sum(value != 0 for value in coordinate_map),
            "transfer_degree": len(transfer) - 1,
            "transfer_support": sum(value != 0 for value in transfer),
            "square_transfer_checks": square_checks,
            "loop_norm_checks": len(cycles),
        })

    gauge_checks = 0
    for seed in (1, 3, 7, 11, 19):
        signs = {
            value: (-1 if ((value * seed + value // 2) % 5 in (1, 2)) else 1)
            for value in representatives
        }
        signs[representatives[0]] = 1
        signed_roots = {
            value: root_values[value] * signs[value] % p
            for value in representatives
        }
        for multiplier in (2, GLV_LAMBDA[instance.name]):
            cycles = pair_cycles(representatives, multiplier, n)
            signed_transfer: dict[int, int] = {}
            for value in representatives:
                target = even_representative(multiplier * value, n)
                signed_transfer[value] = (
                    signed_roots[target] * pow(signed_roots[value], -1, p) % p
                )
                original = (
                    root_values[target] * pow(root_values[value], -1, p) % p
                )
                if signed_transfer[value] ** 2 % p != original ** 2 % p:
                    raise AssertionError("gauge changed a public transfer square")
                gauge_checks += 1
            for cycle in cycles:
                product = 1
                for value in cycle:
                    product = product * signed_transfer[value] % p
                if product != 1:
                    raise AssertionError("gauge changed a closed-loop product")

    return {
        "instance": instance.name,
        "p": p,
        "n": n,
        "pair_components": pair_count,
        "multipliers": multiplier_rows,
        "anchored_gauge_choices": f"2^{pair_count - 1}",
        "deterministic_gauge_checks": gauge_checks,
        "all_coordinate_maps_dense": all(
            int(row["coordinate_map_support"]) == pair_count
            for row in multiplier_rows
        ),
        "all_transfer_polynomials_dense": all(
            int(row["transfer_support"]) == pair_count
            for row in multiplier_rows
        ),
        "errors": 0,
    }


def build_payload() -> dict[str, object]:
    curves = [curve_replay(instance) for instance in INSTANCES]
    secp_pair_count = (SECP_N - 1) // 2
    factorization = sp.factorint(secp_pair_count)
    if pow(2, secp_pair_count, SECP_N) != 1:
        raise AssertionError("secp doubling order does not divide pair count")
    if any(
        pow(2, secp_pair_count // prime, SECP_N) == 1
        for prime in factorization
    ):
        raise AssertionError("secp doubling order is a proper divisor")

    payload: dict[str, object] = {
        "profile_id": "UORC-056-EQUIVARIANT-TRANSFER-GAUGE-C40",
        "schema_version": "1.0",
        "curves": curves,
        "secp256k1": {
            "n": SECP_N,
            "pair_components": secp_pair_count,
            "order_of_two_on_pair_quotient": secp_pair_count,
            "doubling_action_transitive": True,
            "anchored_public_action_gauge_choices": f"2^{secp_pair_count - 1}",
        },
        "aggregate": {
            "curves": len(curves),
            "pair_components": sum(
                int(row["pair_components"]) for row in curves
            ),
            "deterministic_gauge_checks": sum(
                int(row["deterministic_gauge_checks"]) for row in curves
            ),
            "all_coordinate_maps_dense": all(
                bool(row["all_coordinate_maps_dense"]) for row in curves
            ),
            "all_transfer_polynomials_dense": all(
                bool(row["all_transfer_polynomials_dense"]) for row in curves
            ),
            "errors": 0,
        },
        "theorem": {
            "gauge_action": "R_i -> s_i R_i sends T_gamma(i) to s_(gamma i)s_i T_gamma(i)",
            "preserved_data": "root squares, transfer squares, cocycle laws and all loop products",
            "anchored_freedom": "one fixed component leaves 2^(r-1) coherent root sections",
            "consequence": "public multiplier actions and loop coherence alone do not select parity orientation",
        },
        "decision": {
            "public_action_coherence_selects_orientation": False,
            "cheap_parity_decoder_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["digest"] = hashlib.sha256(canonical).hexdigest()
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    payload = build_payload()
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
    print("UORC056_EQUIVARIANT_TRANSFER_GAUGE_C40_OK")
    print(json.dumps(payload["aggregate"], sort_keys=True))
    print("digest=" + str(payload["digest"]))


if __name__ == "__main__":
    main()
