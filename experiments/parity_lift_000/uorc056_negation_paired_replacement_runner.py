#!/usr/bin/env python3
"""Run one public generator-replacement C20 case."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
MAIN = HERE / "uorc056_negation_paired_quadratic.py"
spec = importlib.util.spec_from_file_location("uorc056_c20_main_replacements", MAIN)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
assert spec.loader is not None
spec.loader.exec_module(mod)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("base_index", type=int)
    parser.add_argument("multiplier", type=int)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.base_index not in (0, 1) or args.multiplier not in (2, 3, 5):
        raise SystemExit("unsupported replacement specification")
    base = mod.c17.public_extension_corpus()[args.base_index]
    p, n = int(base["p"]), int(base["n"])
    new_G = mod.c17.ec_mul(args.multiplier, tuple(base["G"]), p)
    if new_G is None:
        raise AssertionError("bad public generator replacement")
    points = mod.c17.subgroup_points(p, n, new_G)
    target = mod.c17.phi(new_G, int(base["beta"]), p)
    try:
        expected_lam = points.index(target)
    except ValueError as exc:
        raise AssertionError("replacement GLV image missing") from exc
    if expected_lam != int(base["lambda"]):
        raise AssertionError("lambda changed under generator replacement")
    core = {
        "p": p,
        "n": n,
        "G": list(new_G),
        "beta": int(base["beta"]),
        "lambda": int(base["lambda"]),
    }
    row = mod.run_case(core, "generator_replacement")
    row["replacement_metadata"] = {
        "base_index": args.base_index,
        "base_G": list(base["G"]),
        "multiplier": args.multiplier,
        "expected_lambda": expected_lam,
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    path = args.out_dir / f"replacement_{args.base_index}_{args.multiplier}.json"
    path.write_text(json.dumps(row, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "base_index": args.base_index,
        "multiplier": args.multiplier,
        "p": p,
        "n": n,
        "dickson_full_support": row["dickson"]["trace_screen"]["all_screened_traces_have_full_quotient_support"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
