#!/usr/bin/env python3
"""Lightweight C14 replay for the rational fibre-readout gauge law.

Uses only the six frozen C9 curves, known subgroup points, and public generator
replacements. No unknown scalar or external point is accepted.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load_c9():
    path = HERE / "uorc056_primal_orientation_branch.py"
    spec = importlib.util.spec_from_file_location("c9_c14_light", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load C9 dependency")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


c9 = _load_c9()
CONSTANTS = (0, 1, 2, 3, 5)


def inv(value: int, p: int) -> int:
    return pow(value % p, -1, p)


def readout(point: tuple[int, int], p: int) -> int:
    x, y = point
    return (y + 7 * x + 11) % p


def multiplier(point: tuple[int, int], constant: int, p: int) -> int:
    return (point[0] - constant) % p


def verify_generator(case: dict[str, object], generator: tuple[int, int], required: int) -> dict[str, int | bool]:
    p = int(case["p"])
    n = int(case["n"])
    points = c9.subgroup_points(case, generator)
    accepted = 0
    checks = 0
    inverse_checks = 0
    ratio_sets = {constant: set() for constant in CONSTANTS}

    for k in range(1, n - 1):
        P = points[k]
        PG = points[k + 1]
        if P is None or PG is None:
            continue
        rP = readout(P, p)
        rPG = readout(PG, p)
        if rP == 0 or rPG == 0:
            continue
        local = []
        bad = False
        for constant in CONSTANTS:
            uP = multiplier(P, constant, p)
            uPG = multiplier(PG, constant, p)
            if uP == 0 or uPG == 0:
                bad = True
                break
            local.append((constant, uP, uPG))
        if bad:
            continue

        endpoint = rP * inv(rPG, p) % p
        for constant, uP, uPG in local:
            gauge_ratio = uP * inv(uPG, p) % p
            observed = (uP * rP) * inv(uPG * rPG, p) % p
            expected = endpoint * gauge_ratio % p
            assert observed == expected
            assert observed * inv(gauge_ratio, p) % p == endpoint
            ratio_sets[constant].add(gauge_ratio)
            checks += 1
            inverse_checks += 1
        accepted += 1
        if accepted >= required:
            break

    if accepted < required:
        raise AssertionError(f"only {accepted} valid known-scalar points, need {required}")
    nonconstant = sum(1 for values in ratio_sets.values() if len(values) > 1)
    if required > 1 and nonconstant < 3:
        raise AssertionError("insufficient nonconstant gauge families")
    return {
        "accepted_points": accepted,
        "gauge_transformation_checks": checks,
        "inverse_normalization_checks": inverse_checks,
        "nonconstant_gauge_families": nonconstant,
        "passed": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    base_cases = []
    replacements = []
    for index, case in enumerate(c9.FROZEN_CURVES):
        base_G = tuple(case["G"])
        base = verify_generator(case, base_G, required=8)
        base_cases.append({"n": int(case["n"]), "checks": base})

        points = c9.subgroup_points(case, base_G)
        n = int(case["n"])
        multipliers = list(range(1, n)) if index < 3 else sorted({1, 2, 3, 5, n - 1})
        rows = []
        for scalar in multipliers:
            generator = points[scalar]
            if generator is None:
                raise AssertionError("replacement generator is identity")
            rows.append(verify_generator(case, generator, required=3))
        replacements.append({
            "n": n,
            "replacements_checked": len(rows),
            "gauge_transformation_checks": sum(int(row["gauge_transformation_checks"]) for row in rows),
            "inverse_normalization_checks": sum(int(row["inverse_normalization_checks"]) for row in rows),
            "nonconstant_gauge_families": sum(int(row["nonconstant_gauge_families"]) for row in rows),
            "passed": True,
        })

    payload = {
        "experiment": "UORC056_C14_RATIONAL_FIBRE_READOUT_LIGHT_REPLAY",
        "identity": "endpoint(u*R)=endpoint(R)*u(P)/u(P+G)",
        "cases": base_cases,
        "generator_replacements": replacements,
        "aggregate": {
            "curves": len(base_cases),
            "base_gauge_transformation_checks": sum(int(row["checks"]["gauge_transformation_checks"]) for row in base_cases),
            "base_inverse_normalization_checks": sum(int(row["checks"]["inverse_normalization_checks"]) for row in base_cases),
            "base_nonconstant_gauge_families": sum(int(row["checks"]["nonconstant_gauge_families"]) for row in base_cases),
            "generator_replacements_checked": sum(int(row["replacements_checked"]) for row in replacements),
            "replacement_gauge_transformation_checks": sum(int(row["gauge_transformation_checks"]) for row in replacements),
            "replacement_inverse_normalization_checks": sum(int(row["inverse_normalization_checks"]) for row in replacements),
            "replacement_nonconstant_gauge_families": sum(int(row["nonconstant_gauge_families"]) for row in replacements),
            "gauge_transformation_law_verified": True,
            "canonical_weight_one_readout_without_gauge_found": False,
            "sub_sqrt_evaluator_found": False,
        },
    }
    text = json.dumps(payload, indent=2, sort_keys=True)
    print(text)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
