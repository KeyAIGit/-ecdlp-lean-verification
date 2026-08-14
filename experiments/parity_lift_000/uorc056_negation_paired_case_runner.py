#!/usr/bin/env python3
"""Run one C20 public corpus case in an isolated process."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
MAIN = HERE / "uorc056_negation_paired_quadratic.py"
spec = importlib.util.spec_from_file_location("uorc056_c20_main", MAIN)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
assert spec.loader is not None
spec.loader.exec_module(mod)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("index", type=int)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    corpus = mod.c17.public_extension_corpus()
    if not 0 <= args.index < len(corpus):
        raise SystemExit("case index out of range")
    core = corpus[args.index]
    split = mod.CORPUS_SPLIT[int(core[0])]
    row = mod.run_case(core, split)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    path = args.out_dir / f"case_{args.index}.json"
    path.write_text(json.dumps(row, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "index": args.index,
        "p": row["p"],
        "n": row["n"],
        "split": row["split"],
        "pair_exceptions": row["pair_exception_count"],
        "dickson_full_support": row["dickson"]["trace_screen"]["all_screened_traces_have_full_quotient_support"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
