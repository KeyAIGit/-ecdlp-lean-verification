#!/usr/bin/env python3
"""Public generator-replacement replay for UORC056 C19."""
from __future__ import annotations
import argparse
import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
MODULE = HERE / "uorc056_odd_rational_functional_boundary.py"
spec = importlib.util.spec_from_file_location("uorc056_c19", MODULE)
mod = importlib.util.module_from_spec(spec)
sys.modules["uorc056_c19"] = mod
assert spec.loader is not None
spec.loader.exec_module(mod)


def run_replacement(base_case, multiplier: int):
    p, n, G, beta, lam = base_case
    base_context = mod.c17.RFContext(p, G, beta)
    base_points = base_context.points(n)
    replacement = base_points[multiplier % n]
    if replacement is None:
        raise AssertionError("zero replacement")
    C = mod.c17.RFContext(p, replacement, beta)
    points = C.points(n)
    target = (beta * replacement[0] % p, replacement[1])
    replacement_lambda = points.index(target)
    if replacement_lambda != lam:
        raise AssertionError("GLV eigenvalue changed under generator replacement")
    Z, endpoint = mod.endpoint_function(C, n, points)
    conjugates = [Z, C.rf_phi(Z)]
    conjugates.append(C.rf_phi(conjugates[-1]))
    trace = C.rf_add(C.rf_add(conjugates[0], conjugates[1]), conjugates[2])
    parity = [1 if k % 2 == 0 else -1 for k in range(n)]
    correction = {k for k in range(1, n) if endpoint[k] != parity[k]}
    rows = mod.orbit_rows(n, lam, correction)
    for row in rows:
        point = points[row["representative"]]
        row["point"] = point
        row["series"] = [
            mod.ls_from_dict(C.series_laurent(z, point, K=mod.SERIES_TERMS), p)
            for z in conjugates
        ]
        if any(series is None for series in row["series"]):
            raise AssertionError("replacement series vanished to truncation")
    ratio = mod.ratio_spectrum(rows, p)
    families = mod.one_parameter_exact_screens(C, rows, conjugates)
    reciprocity = mod.compact_negation_reciprocity(C, n, endpoint, Z, trace, points)
    return {
        "p": p,
        "n": n,
        "base_G": list(G),
        "multiplier": multiplier,
        "replacement_G": list(replacement),
        "lambda": lam,
        "endpoint_correction_indices": sorted(correction),
        "ratio_spectrum": ratio,
        "one_parameter_screens": families,
        "negation_reciprocity": reciprocity,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=pathlib.Path, required=True)
    args = parser.parse_args()
    corpus = mod.c17.public_extension_corpus(2)
    rows = [run_replacement(case, u) for case in corpus for u in (2, 3, 5)]
    payload = {
        "experiment": "ODD-RATIONAL-FUNCTIONAL-CALCULUS-069-C19-GENERATOR-REPLACEMENTS",
        "replacement_rule": "u in {2,3,5} on the first two public extension curves",
        "cases": rows,
        "aggregate": {
            "replacements": len(rows),
            "all_lambda_covariance_checks_pass": True,
            "all_compact_negation_products_degree_1_over_3": all(
                row["negation_reciprocity"]["K_signature"]["degrees"] == [1, 0, 3]
                for row in rows
            ),
            "all_compact_negation_products_support_at_most_9": all(
                row["negation_reciprocity"]["K_divisor_support_size"] <= 9 for row in rows
            ),
            "all_s1_ratio_spectra_nonconstant": all(
                row["ratio_spectrum"]["1"]["distinct_cancellation_ratios"] > 1 for row in rows
            ),
            "balanced_subsqrt_divisor_support_found": False,
            "parity_oracle_found": False,
        },
    }
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
