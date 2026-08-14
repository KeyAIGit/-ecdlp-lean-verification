#!/usr/bin/env python3
from __future__ import annotations
import argparse
import importlib.util
import json
import pathlib
import pickle
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
MODULE = HERE / "uorc056_odd_rational_functional_boundary.py"
spec = importlib.util.spec_from_file_location("uorc056_c19", MODULE)
mod = importlib.util.module_from_spec(spec)
sys.modules["uorc056_c19"] = mod
assert spec.loader is not None
spec.loader.exec_module(mod)

parser = argparse.ArgumentParser()
parser.add_argument("case_index", type=int, choices=range(7))
parser.add_argument("--out-dir", type=pathlib.Path, default=HERE)
args = parser.parse_args()
args.out_dir.mkdir(parents=True, exist_ok=True)

cases = mod.c17.public_extension_corpus(7)
start = time.time()
result, metrics = mod.run_case(cases[args.case_index], mod.all_templates())
(args.out_dir / f"case_{args.case_index}.json").write_text(
    json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
with (args.out_dir / f"metrics_{args.case_index}.pkl").open("wb") as handle:
    pickle.dump(metrics, handle)
print(json.dumps({
    "case_index": args.case_index,
    "p": result["p"],
    "n": result["n"],
    "seconds": round(time.time() - start, 3),
    "minimum_metric": result["bounded_synthesis"]["minimum_metric_support_poles_uncertain"],
}, sort_keys=True))
