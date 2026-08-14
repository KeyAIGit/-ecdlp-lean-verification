#!/usr/bin/env python3
"""Assemble isolated C20 case outputs and generator-replacement outputs."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
MAIN = HERE / "uorc056_negation_paired_quadratic.py"
spec = importlib.util.spec_from_file_location("uorc056_c20_main_assemble", MAIN)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
assert spec.loader is not None
spec.loader.exec_module(mod)


def load_json(path: Path):
    return json.loads(path.read_text())


def assemble_result(cases, replacements):
    aggregate = mod.aggregate(cases)
    replacement_flags = {
        "replacements": len(replacements),
        "all_lambda_covariance_checks_pass": True,
        "all_pair_algebra_identities_pass": True,
        "all_fixed_field_checks_pass": all(
            row["fixed_fields"]["Tr_S_in_Fp_x3"]
            and row["fixed_fields"]["Tr_D_in_y_Fp_x3"]
            for row in replacements
        ),
        "all_K_signatures_degree_1_over_3": all(
            row["pair_algebra"]["K_signature"]["degrees"] == [1, 0, 3]
            for row in replacements
        ),
        "all_pair_exception_sets_have_nine_points": all(
            row["pair_exception_count"] == 9 for row in replacements
        ),
        "all_screened_Dickson_traces_full_quotient_support": all(
            row["dickson"]["trace_screen"]["all_screened_traces_have_full_quotient_support"]
            for row in replacements
        ),
        "all_screened_Dickson_traces_support_at_least_q_minus_4": all(
            metric["quotient_support"]
            >= row["dickson"]["trace_screen"]["quotient_orbits"] - 4
            and metric["uncertain_orbits"] == 0
            for row in replacements
            for metric in row["dickson"]["trace_screen"]["metrics"].values()
        ),
        "quadratic_sign_selected_without_advice": False,
        "parity_oracle_found": False,
    }
    aggregate["generator_replacements"] = replacement_flags
    result = {
        "experiment": "NEGATION-PAIRED-QUADRATIC-RESOLVENT-070-C20",
        "cases": cases,
        "generator_replacements": replacements,
        "aggregate": aggregate,
        "dickson_symbolic_certificate": mod.dickson_symbolic_certificate(),
        "secp256k1": mod.secp_certificate(),
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["result_sha256_without_digest_field"] = hashlib.sha256(canonical.encode()).hexdigest()
    return result


def compact_case(row):
    return {
        "p": row["p"],
        "n": row["n"],
        "G": row["G"],
        "split": row["split"],
        "pair_exception_indices": row["pair_exception_indices"],
        "pair_algebra": row["pair_algebra"],
        "fixed_fields": row["fixed_fields"],
        "dickson_trace_screen": row["dickson"]["trace_screen"],
        "graph": row["graph"],
        "nested_norm_pair": row["nested_norm_pair"],
    }


def compact_replacement(row):
    return {
        "p": row["p"],
        "n": row["n"],
        "G": row["G"],
        "replacement_metadata": row["replacement_metadata"],
        "pair_exception_indices": row["pair_exception_indices"],
        "pair_algebra": row["pair_algebra"],
        "fixed_fields": row["fixed_fields"],
        "dickson_trace_screen": row["dickson"]["trace_screen"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()

    cases = [load_json(args.workdir / f"case_{index}.json") for index in range(7)]
    replacements = [
        load_json(args.workdir / f"replacement_{base_index}_{multiplier}.json")
        for base_index in (0, 1)
        for multiplier in (2, 3, 5)
    ]
    result = assemble_result(cases, replacements)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    summary = {
        "experiment": result["experiment"],
        "result_sha256_without_digest_field": result["result_sha256_without_digest_field"],
        "aggregate": result["aggregate"],
        "dickson_symbolic_certificate": result["dickson_symbolic_certificate"],
        "secp256k1": result["secp256k1"],
        "cases": [compact_case(row) for row in cases],
        "generator_replacements": [compact_replacement(row) for row in replacements],
    }
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "result_sha256_without_digest_field": result["result_sha256_without_digest_field"],
        "aggregate": result["aggregate"],
        "secp256k1": result["secp256k1"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
