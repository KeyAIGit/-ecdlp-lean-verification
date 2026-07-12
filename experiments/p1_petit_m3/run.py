#!/usr/bin/env python3
"""P1-m3 driver: measure the S4 (3-term) relation-SOLVING step across toy curves.

For each (variant, bits, N) it builds the curve (cofactor-1 generator from P0), the factor
base (plain-x vs GLV-orbit / u=x^3-closed at MATCHED effective size N), draws T random
targets R = k*G, and for each target solves S4(x_i, x_j, X, x_R)=0 over every base pair
(Theta(N^2) degree-<=4 field-solves, NOT the O(N^3) triple enumeration). Every confirmed
3-term relation is re-checked by actual EC addition over the 8 sign patterns; spurious roots
(S4 roots in the base that fail every sign-lift) are counted separately.

Provenance is recorded with the P0 ``manifest.py`` helper (reused, retargeted to this
experiment's runs/ directory): git commit, seed, params, tool versions, code hashes, an
output hash, and a real UTC timestamp.

HONESTY: this reports ONLY measured numbers for the sizes actually run. No growth fit, no
asymptotic claim, and no advantage / no-advantage conclusion is produced here. GLV vs plain
is reported as raw measured counts at matched effective base size. The O(|F|^2) pair-loop
over a degree-4 solve is NOT a subexponential index-calculus algorithm; see RESULTS.md.
"""
from __future__ import annotations

import sys
import time
from datetime import datetime, timezone
from math import isqrt
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_P0 = _HERE.parent / "p0_glv_semaev"
_P1 = _HERE.parent / "p1_petit"
for _d in (_P0, _P1):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))

import random  # noqa: E402

from toy_curves import find_toy_curve, ec_mul  # noqa: E402
import manifest as p0manifest  # noqa: E402
from semaev_solve import build_plain_base, build_glv_base  # noqa: E402

from semaev4_solve import search_relations3  # noqa: E402

# Retarget the reused manifest helper to THIS experiment's runs/ directory.
p0manifest.RUNS = _HERE / "runs"

SEED = 1


def run_setting(bits: int, N: int, variant: str, T: int) -> dict:
    """One measurement: build curve+base, run T targets, accumulate S4-solve metrics."""
    C = find_toy_curve(bits, seed=SEED, require_cofactor_one=True)
    if variant == "plain":
        fb = build_plain_base(C, N)
    elif variant == "glv-orbit":
        fb = build_glv_base(C, N)
    else:
        raise ValueError(variant)

    rng = random.Random(2000 + bits * 7 + N + (0 if variant == "plain" else 1))
    total_pair_solves = 0
    roots_total = 0
    roots_in_base = 0
    confirmed_relations = 0
    spurious_total = 0
    s4_nonzero_total = 0
    degenerate_pairs = 0
    targets_with_relation = 0
    example = None

    t0 = time.time()
    for _ in range(T):
        k = rng.randrange(1, C.ell)
        R = ec_mul(k, C.gen, 0, C.p)
        if R is None:
            continue
        res = search_relations3(C, fb, R)
        total_pair_solves += res["pair_solves"]
        roots_total += res["roots_total"]
        roots_in_base += res["roots_in_base"]
        spurious_total += res["spurious"]
        s4_nonzero_total += res["s4_nonzero"]
        degenerate_pairs += res["degenerate_pairs"]
        n_conf = len(res["confirmed_triples"])
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
        "total_pair_solves": total_pair_solves,
        "roots_total": roots_total,
        "roots_in_base": roots_in_base,
        "confirmed_relations": confirmed_relations,
        "spurious_roots": spurious_total,
        "s4_nonzero_roots": s4_nonzero_total,
        "degenerate_pairs": degenerate_pairs,
        "targets_with_relation": targets_with_relation,
        "yield_relations_per_target": confirmed_relations / T if T else 0.0,
        "hit_rate": targets_with_relation / T if T else 0.0,
        "solves_per_confirmed_relation": (total_pair_solves / confirmed_relations)
        if confirmed_relations else None,
        "spurious_rate": (spurious_total / roots_in_base) if roots_in_base else 0.0,
        "wall_time_s": round(dt, 3),
        "example_relation": example,
    }


def main():
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    # (bits, N, T): N a multiple of 3 (GLV orbit size); sizes/targets chosen for a small
    # honest measurement (correctness + cross-check over breadth), staying well under the
    # cofactor-1 subgroup and finishing in a few minutes on one core.
    grid = [
        (16, 18, 300),
        (16, 36, 150),
        (20, 24, 200),
        (20, 48, 100),
        (24, 48, 60),
    ]
    measurements = []
    for bits, N, T in grid:
        for variant in ("plain", "glv-orbit"):
            m = run_setting(bits, N, variant, T)
            measurements.append(m)
            spr = m["solves_per_confirmed_relation"]
            spr_s = f"{spr:.0f}" if spr is not None else "  n/a"
            print(f"[{variant:9s} {bits:2d}b N={N:3d} T={T:4d}] "
                  f"distinctX={m['n_distinct_x']:3d} orbits={m['n_orbits']:3d} "
                  f"store={m['storage_units']:3d} | pairSolves={m['total_pair_solves']:8d} "
                  f"conf={m['confirmed_relations']:4d} hitTgts={m['targets_with_relation']:4d} "
                  f"spur={m['spurious_roots']:3d} rootsInBase={m['roots_in_base']:5d} "
                  f"y/tgt={m['yield_relations_per_target']:.4f} "
                  f"solves/rel={spr_s} {m['wall_time_s']}s")

    man = p0manifest.Manifest(
        hypothesis="HYP_GLV_SEMAEV_001",
        variant="p1m3-semaev4-solve",
        params={"seed": SEED,
                "grid": [[b, n, t] for b, n, t in grid],
                "method": "S4 = Res_Y(S3,S3); degree-<=4 F_p root solve; 8-sign EC-confirmed"},
        code_files=[str(_HERE / "semaev4_solve.py"),
                    str(_HERE / "run.py"),
                    str(_P1 / "semaev_solve.py"),
                    str(_P0 / "toy_curves.py")],
    )
    man.record({"measurements": measurements})
    path = man.write(timestamp)
    print(f"\nmanifest: {path}")
    return measurements, path


if __name__ == "__main__":
    main()
