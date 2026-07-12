#!/usr/bin/env python3
"""P1 driver: measure the S3-SOLVING 2-term relation step across toy curves.

For each (variant, bits, N) it builds the curve (corrected cofactor-1 generator from P0),
the factor base (plain-x vs GLV-orbit/u=x^3-closed at MATCHED effective size N), draws T
random targets R = k*G, and for each target solves S3(x_i, X, x_R)=0 over the base
(O(N) field-solves, NOT O(N^2) enumeration). Every confirmed relation is re-checked by
actual EC addition; spurious roots (S3 roots in the base that fail the EC sign-lift) are
counted separately.

Provenance is recorded with the P0 ``manifest.py`` helper (reused, retargeted to this
experiment's runs/ directory): git commit, seed, params, tool versions, code hashes, an
output hash, and a real UTC timestamp.

Honesty: this reports ONLY measured numbers for the sizes actually run. No growth fit,
no asymptotic claim, no "advantage/no-advantage" conclusion is produced here.
"""
from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timezone
from math import isqrt
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_P0 = _HERE.parent / "p0_glv_semaev"
if str(_P0) not in sys.path:
    sys.path.insert(0, str(_P0))

import random  # noqa: E402

from toy_curves import find_toy_curve, ec_mul  # noqa: E402
import manifest as p0manifest  # noqa: E402

from semaev_solve import build_plain_base, build_glv_base, search_relations  # noqa: E402

# Retarget the reused manifest helper to THIS experiment's runs/ directory.
p0manifest.RUNS = _HERE / "runs"

SEED = 1


def run_setting(bits: int, N: int, variant: str, T: int) -> dict:
    """One measurement: build curve+base, run T targets, accumulate S3-solve metrics."""
    C = find_toy_curve(bits, seed=SEED, require_cofactor_one=True)
    if variant == "plain":
        fb = build_plain_base(C, N)
    elif variant == "glv-orbit":
        fb = build_glv_base(C, N)
    else:
        raise ValueError(variant)

    rng = random.Random(1000 + bits * 7 + N + (0 if variant == "plain" else 1))
    total_solves = 0
    roots_total = 0
    roots_in_base = 0
    confirmed_relations = 0
    spurious_total = 0
    s3_nonzero_total = 0
    targets_with_relation = 0
    example = None

    t0 = time.time()
    for _ in range(T):
        k = rng.randrange(1, C.ell)
        R = ec_mul(k, C.gen, 0, C.p)
        if R is None:
            continue
        res = search_relations(C, fb, R)
        total_solves += res["solves"]
        roots_total += res["roots_total"]
        roots_in_base += res["roots_in_base"]
        spurious_total += res["spurious"]
        s3_nonzero_total += res["s3_nonzero"]
        n_conf = len(res["confirmed_pairs"])
        confirmed_relations += n_conf
        if n_conf:
            targets_with_relation += 1
        if example is None and res["example"] is not None:
            example = dict(res["example"])
            example["k"] = k
    dt = time.time() - t0

    return {
        "variant": variant,
        "bits": bits,
        "p": C.p,
        "b": C.b,
        "order": C.order,
        "ell": C.ell,
        "cofactor": C.cofactor,
        "generator": list(C.gen),
        "beta": C.beta,
        "lambda": C.lam,
        "sqrt_p": isqrt(C.p),
        "N_requested": N,
        "base_size": fb.n_distinct_x,       # keyed for validate_run compatibility
        "n_distinct_x": fb.n_distinct_x,
        "n_orbits": fb.n_orbits,
        "storage_units": fb.storage_units,
        "trials": T,
        "total_field_solves": total_solves,
        "roots_total": roots_total,
        "roots_in_base": roots_in_base,
        "confirmed_relations": confirmed_relations,
        "spurious_roots": spurious_total,
        "s3_nonzero_roots": s3_nonzero_total,
        "targets_with_relation": targets_with_relation,
        "yield_relations_per_target": confirmed_relations / T if T else 0.0,
        "hit_rate": targets_with_relation / T if T else 0.0,
        "solves_per_confirmed_relation": (total_solves / confirmed_relations)
        if confirmed_relations else None,
        "spurious_rate": (spurious_total / roots_in_base) if roots_in_base else 0.0,
        "wall_time_s": round(dt, 3),
        "example_relation": example,
    }


def main():
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    T = 2000
    # (bits, N) with N a multiple of 3 (GLV orbit size); sizes chosen to stay
    # unsaturated at these p while giving nonzero relation counts.
    grid = [
        (16, 48), (16, 96),
        (20, 192), (20, 384),
        (24, 384), (24, 768),
    ]
    measurements = []
    for bits, N in grid:
        for variant in ("plain", "glv-orbit"):
            m = run_setting(bits, N, variant, T)
            measurements.append(m)
            print(f"[{variant:9s} {bits:2d}b N={N:4d}] "
                  f"distinctX={m['n_distinct_x']:4d} orbits={m['n_orbits']:4d} "
                  f"store={m['storage_units']:4d} | solves={m['total_field_solves']:8d} "
                  f"conf={m['confirmed_relations']:5d} spur={m['spurious_roots']:4d} "
                  f"rootsInBase={m['roots_in_base']:5d} "
                  f"y/tgt={m['yield_relations_per_target']:.4f} "
                  f"solves/rel={m['solves_per_confirmed_relation']} "
                  f"{m['wall_time_s']}s")

    man = p0manifest.Manifest(
        hypothesis="HYP_GLV_SEMAEV_001",
        variant="p1-semaev-solve",
        params={"seed": SEED, "trials": T,
                "grid": [[b, n] for b, n in grid],
                "method": "S3 quadratic solve (Tonelli-Shanks), EC-confirmed"},
        code_files=[str(_HERE / "semaev_solve.py"),
                    str(_HERE / "run.py"),
                    str(_P0 / "toy_curves.py")],
    )
    man.record({"measurements": measurements})
    path = man.write(timestamp)
    print(f"\nmanifest: {path}")
    return measurements, path


if __name__ == "__main__":
    main()
