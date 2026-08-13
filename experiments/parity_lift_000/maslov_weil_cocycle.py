#!/usr/bin/env python3
"""Toy-only exact Maslov/Weil cocycle replay built on C053 theta lifts.

No external point, key, wallet or production target is accepted.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from metaplectic_theta_intertwiner import (
    CASES,
    Fp3,
    affine_pencil_screen,
    build_case,
    characteristic_features,
    quadratic_character,
)


def minor(v, w, a, b):
    return v[a] * w[b] - v[b] * w[a]


def det3(cols):
    a, b, c = cols
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - b[0] * (a[1] * c[2] - a[2] * c[1])
        + c[0] * (a[1] * b[2] - a[2] * b[1])
    )


def build_rows(p, n, generator):
    points, beta, lam, carry = build_case(p, n, generator)
    cache = {}
    rows = []
    exceptions = []
    descent_checks = 0
    edge_relation_checks = 0

    for scalar in range(1, n):
        scalars = [scalar, (scalar + 1) % n, (scalar + 1 + lam) % n]
        if 0 in scalars:
            exceptions.append({"scalar": scalar, "reason": "triangle_vertex_infinity"})
            continue

        theta = []
        xs = []
        for index in scalars:
            point = points[index]
            assert point is not None
            x, _y = point
            xs.append(x)
            if x not in cache:
                cache[x] = characteristic_features(x, p, beta)
            theta.append(cache[x]["theta"])

        dx = [
            (xs[1] - xs[0]) % p,
            (xs[2] - xs[1]) % p,
            (xs[0] - xs[2]) % p,
        ]
        if 0 in dx:
            exceptions.append({"scalar": scalar, "reason": "triangle_x_collision"})
            continue

        dx_product = dx[0] * dx[1] % p * dx[2] % p
        point = points[scalar]
        assert point is not None
        row = {
            "scalar": scalar,
            "g": int(carry[scalar]),
            "h": int(carry[scalar]) * quadratic_character(point[1], p),
            "Dx": dx_product,
        }

        volume = det3(theta)
        assert volume.is_base_field()
        descent_checks += 1
        row["V012"] = volume.base_value()

        for a, b, name in ((0, 1, "01"), (0, 2, "02"), (1, 2, "12")):
            determinants = [
                minor(theta[0], theta[1], a, b),
                minor(theta[1], theta[2], a, b),
                minor(theta[2], theta[0], a, b),
            ]
            maslov = determinants[0] * determinants[1] * determinants[2]
            assert maslov.is_base_field()
            descent_checks += 1
            row["Mu" + name] = maslov.base_value()

            normalized = (
                determinants[0] / Fp3(dx[0], 0, 0, p)
                * determinants[1] / Fp3(dx[1], 0, 0, p)
                * determinants[2] / Fp3(dx[2], 0, 0, p)
            )
            assert normalized.is_base_field()
            descent_checks += 1
            normalized_value = normalized.base_value()
            row["R" + name] = normalized_value

            edge_cube_product = 1
            for determinant, difference in zip(determinants, dx):
                edge_cube_product = (
                    edge_cube_product
                    * ((determinant / Fp3(difference, 0, 0, p)) ** 3).base_value()
                ) % p
            assert pow(normalized_value, 3, p) == edge_cube_product
            assert maslov.base_value() == normalized_value * dx_product % p
            edge_relation_checks += 2

        if any(
            row[name] == 0
            for name in ("V012", "Mu01", "Mu02", "Mu12", "R01", "R02", "R12", "Dx")
        ):
            exceptions.append({"scalar": scalar, "reason": "cocycle_zero"})
            continue
        rows.append(row)

    return points, beta, lam, carry, rows, exceptions, descent_checks, edge_relation_checks


def screen_case(p, n, generator):
    points, beta, lam, _carry, rows, exceptions, descent_checks, edge_relation_checks = build_rows(
        p, n, generator
    )
    features = ["V012", "Mu01", "Mu02", "Mu12", "R01", "R02", "R12", "Dx", "1"]
    arrays = {
        name: np.array([1 if name == "1" else row[name] for row in rows], dtype=np.int64)
        for name in features
    }
    targets = {
        name: np.array([row[name] for row in rows], dtype=np.int8)
        for name in ("g", "h")
    }
    formulas, exact, best = affine_pencil_screen(p, arrays, targets)

    characters = np.zeros(p, dtype=np.int8)
    for value in range(1, p):
        characters[value] = quadratic_character(value, p)

    subset_exact = []
    subset_best = {"g": 0.0, "h": 0.0}
    base_features = features[:-1]
    for mask in range(1, 1 << len(base_features)):
        values = np.ones(len(rows), dtype=np.int64)
        names = []
        for index, name in enumerate(base_features):
            if (mask >> index) & 1:
                values = values * arrays[name] % p
                names.append(name)
        signs = characters[values]
        for target_name, target in targets.items():
            positive = int((signs == target).sum())
            negative = int((-signs == target).sum())
            subset_best[target_name] = max(
                subset_best[target_name], positive / len(rows), negative / len(rows)
            )
            if positive == len(rows):
                subset_exact.append({"target": target_name, "features": names, "global_sign": 1})
            if negative == len(rows):
                subset_exact.append({"target": target_name, "features": names, "global_sign": -1})

    cocycle_checks = 0
    for start in range(min(12, len(rows) - 3)):
        scalars = [rows[start + offset]["scalar"] for offset in range(4)]
        vectors = []
        cache = {}
        for scalar in scalars:
            point = points[scalar]
            assert point is not None
            x = point[0]
            if x not in cache:
                cache[x] = characteristic_features(x, p, beta)
            vectors.append(cache[x]["theta"])
        for a, b in ((0, 1), (0, 2), (1, 2)):
            bracket = lambda i, j: minor(vectors[i], vectors[j], a, b)
            required = ((0, 1), (1, 2), (2, 0), (0, 2), (2, 3), (3, 0), (0, 3), (1, 3), (3, 1))
            if any(bracket(i, j) == Fp3(0, 0, 0, p) for i, j in required):
                continue
            mu012 = bracket(0, 1) * bracket(1, 2) * bracket(2, 0)
            mu023 = bracket(0, 2) * bracket(2, 3) * bracket(3, 0)
            mu013 = bracket(0, 1) * bracket(1, 3) * bracket(3, 0)
            mu123 = bracket(1, 2) * bracket(2, 3) * bracket(3, 1)
            ratio = mu012 * mu023 / (mu013 * mu123)
            expected = (bracket(0, 2) / bracket(1, 3)) ** 2
            assert ratio == expected
            cocycle_checks += 1

    return {
        "p": p,
        "n": n,
        "generator": list(generator),
        "lambda": lam,
        "screened_points": len(rows),
        "public_exceptions": exceptions,
        "descent_checks": descent_checks,
        "edge_relation_checks": edge_relation_checks,
        "projective_cocycle_checks": cocycle_checks,
        "affine_formula_instances": formulas,
        "affine_exact_decoders": exact,
        "affine_best_accuracy": best,
        "subset_exact_decoders": subset_exact,
        "subset_best_accuracy": subset_best,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--orders", nargs="*", type=int, default=list(CASES))
    parser.add_argument("--out")
    args = parser.parse_args()
    unknown = sorted(set(args.orders) - set(CASES))
    if unknown:
        raise SystemExit(f"orders not frozen: {unknown}")

    cases = [screen_case(*CASES[order]) for order in args.orders]
    result = {
        "schema_version": 1,
        "scope": "toy-only state-dependent Maslov/Weil cocycle screen; no external or production target",
        "object": "Mu_ab=det(v0,v1)det(v1,v2)det(v2,v0) on Q,Q+G,Q+G+phi(G)",
        "cases": cases,
        "aggregate_affine_formula_instances": sum(
            case["affine_formula_instances"] for case in cases
        ),
        "aggregate_exact_decoders": sum(
            len(case["affine_exact_decoders"]) + len(case["subset_exact_decoders"])
            for case in cases
        ),
        "claim_boundary": (
            "Canonical oriented Heisenberg intertwiners have trivial loop monodromy; "
            "this state-dependent projective cocycle is not a scalar-recovery construction."
        ),
    }
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
