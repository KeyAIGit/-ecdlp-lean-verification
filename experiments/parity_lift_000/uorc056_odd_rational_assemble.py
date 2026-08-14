#!/usr/bin/env python3
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import pathlib
import pickle
import sys

HERE = pathlib.Path(__file__).resolve().parent
MODULE = HERE / "uorc056_odd_rational_functional_boundary.py"
spec = importlib.util.spec_from_file_location("uorc056_c19", MODULE)
mod = importlib.util.module_from_spec(spec)
sys.modules["uorc056_c19"] = mod
assert spec.loader is not None
spec.loader.exec_module(mod)

parser = argparse.ArgumentParser()
parser.add_argument("--workdir", type=pathlib.Path, required=True)
parser.add_argument("--out", type=pathlib.Path, required=True)
parser.add_argument("--summary", type=pathlib.Path, required=True)
args = parser.parse_args()

cases = [json.loads((args.workdir / f"case_{i}.json").read_text()) for i in range(7)]
metrics = []
for i in range(7):
    with (args.workdir / f"metrics_{i}.pkl").open("rb") as handle:
        metrics.append(pickle.load(handle))
templates = mod.all_templates()

payload = {
    "experiment": "ODD-RATIONAL-FUNCTIONAL-CALCULUS-069-C19",
    "scope": "public seven-curve j=0 extension corpus and public secp256k1 constants only",
    "normal_forms": ["T*A(T^2)/B(T^2)", "A(T^2)/(T*B(T^2))"],
    "local_order_formulas": {
        "T*A(T2)/B(T2)": {
            "ord_0": "1+2(ord_0(A)-ord_0(B))",
            "ord_infinity": "2deg(B)-2deg(A)-1",
        },
        "A(T2)/(T*B(T2))": {
            "ord_0": "-1+2(ord_0(A)-ord_0(B))",
            "ord_infinity": "2deg(B)-2deg(A)+1",
        },
    },
    "bounded_synthesis_grammar": {
        "forms": [
            "T*(1+a1 U+a2 U^2)/(1+b1 U+b2 U^2)",
            "(1+a1 U+a2 U^2)/(T*(1+b1 U+b2 U^2))",
        ],
        "U": "T^2",
        "coefficient_alphabet": list(mod.COEFF_ALPHABET),
        "templates": len(templates),
        "series_terms": mod.SERIES_TERMS,
    },
    "cases": cases,
    "transfer_screen": mod.aggregate_transfer(cases, metrics, templates),
    "secp256k1": mod.secp_certificate(),
    "bounded_synthesis_audit": {
        "all_template_orbit_valuations_resolved_within_series_window": all(
            metric["uncertain_orbits"] == 0
            for per_case in metrics for metric in per_case.values()
        ),
        "templates_with_uncertain_orbits": sum(
            metric["uncertain_orbits"] > 0
            for per_case in metrics for metric in per_case.values()
        ),
        "total_template_curve_instances": len(templates) * len(cases),
    },
    "aggregate": mod.theorem_flags(cases),
}
canonical = json.dumps(payload, indent=2, sort_keys=True)
digest = hashlib.sha256(canonical.encode()).hexdigest()
payload["result_sha256_without_digest_field"] = digest
args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
summary = {
    "experiment": payload["experiment"],
    "scope": payload["scope"],
    "bounded_synthesis_grammar": payload["bounded_synthesis_grammar"],
    "result_sha256_without_digest_field": digest,
    "aggregate": payload["aggregate"],
    "bounded_synthesis_audit": payload["bounded_synthesis_audit"],
    "secp256k1": payload["secp256k1"],
    "transfer_screen": payload["transfer_screen"],
    "cases": [
        {key: row[key] for key in (
            "p", "n", "G", "beta", "lambda", "parity_orbit_counts",
            "endpoint_correction_indices", "exceptional_orbits", "ratio_spectrum",
            "one_parameter_screens", "negation_reciprocity", "bounded_synthesis",
        )}
        for row in cases
    ],
}
args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({"result_sha256_without_digest_field": digest, "aggregate": payload["aggregate"]}, indent=2, sort_keys=True))
