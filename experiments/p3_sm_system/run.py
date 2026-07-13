#!/usr/bin/env python3
"""P3 driver: build and Groebner-solve the ACTUAL m-term Semaev relation SYSTEM and
measure its degree of regularity, Macaulay matrix dimensions, relations found, relation
probability, and the wall-time split (T_relations + T_solve + T_linear_algebra).

For each configuration (field size p, factor-base size N, m, coordinate system):

  * DEGREE-OF-REGULARITY block: build the relation system for ONE representative
    consistent target R = P_a + P_b (+ P_c) (a target guaranteed to carry a relation),
    Groebner-solve it, and run the independent graded Macaulay engine to measure the
    solving degree / degree of regularity, the largest Macaulay matrix (rows x cols), and
    the quotient dimension. Timings are split T_relations (system build) + T_solve
    (Groebner variety) + T_linear_algebra (Macaulay degree-graded reduction).

  * RELATION-PROBABILITY block: draw T random targets R = k*G, solve the system for each,
    count EC-CONFIRMED relations and (separately) spurious solver outputs, and report the
    relation probability (targets with >=1 relation) / T.

HONESTY (see RESULTS.md): only measured numbers for sizes actually run. No asymptotic or
advantage claim. Any exponent fit is DESCRIPTIVE-ONLY and computed in RESULTS.md, not here.
Every relation is re-verified by real EC addition inside search_relations_system; the
independent anti-overclaim gate is validate.py (brute-force EC, no solver imports).

Provenance via the P0 manifest.py helper (git commit, seed, params, tool versions, code
hashes, output hash, real UTC timestamp).
"""
from __future__ import annotations

import os
import random
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

from toy_curves import find_toy_curve, ec_add, ec_mul  # noqa: E402
from semaev_solve import build_plain_base, build_glv_base  # noqa: E402
import manifest as p0manifest  # noqa: E402

from semaev_system import (search_relations_system, build_plain_system,  # noqa: E402
                           build_invariant_system, grevlex_gb_max_degree)

p0manifest.RUNS = _HERE / "runs"
SEED = 1


def _curve_fields(C, N, fb):
    return {
        "bits": C.bits, "p": C.p, "b": C.b, "order": C.order, "ell": C.ell,
        "cofactor": C.cofactor, "generator": list(C.gen), "beta": C.beta,
        "lambda": C.lam, "sqrt_p": isqrt(C.p), "N_requested": N,
        "base_size": fb.n_distinct_x, "n_distinct_x": fb.n_distinct_x,
        "n_orbits": fb.n_orbits, "storage_units": fb.storage_units,
    }


def _consistent_target(C, fb, m):
    """R = P_0 + ... + P_{m-1} on the base (guaranteed to carry an m-term relation)."""
    R = None
    for idx in range(m):
        R = ec_add(R, fb.points[idx], 0, C.p)
    return R


def dreg_setting(bits, N, m, coord, dreg_max):
    """One degree-of-regularity measurement on a representative consistent target."""
    C = find_toy_curve(bits, seed=SEED, require_cofactor_one=True)
    fb = build_glv_base(C, N) if coord == "invariant" else build_plain_base(C, N)
    R = _consistent_target(C, fb, m)
    res = search_relations_system(C, fb, m, R, coord, measure_dreg=True, dreg_max=dreg_max)
    d = res["d_reg"]
    # cheap complementary measurement: reduced grevlex GB OUTPUT degree + basis size.
    # NOTE: this is the max degree of the final reduced basis, which is SMALL and is NOT
    # the solving degree; the solving degree (max degree reached in the graded computation)
    # is d_reg above. Both are reported so the distinction is explicit.
    F = [P[0] for P in fb.points]
    if coord == "invariant":
        uvals = sorted({(x ** 3) % C.p for x in F})
        sysb = build_invariant_system(m, F, uvals, R[0], C.b, C.p)
    else:
        sysb = build_plain_system(m, F, R[0], C.b, C.p)
    gb_out_deg, gb_basis, gb_time = grevlex_gb_max_degree(sysb.gens, sysb.solve_vars, C.p)
    macaulay_bound = sum(d["gen_degrees"]) - res["nvars"] + 1
    out = dict(_curve_fields(C, N, fb))
    out.update({
        "block": "degree_of_regularity", "m": m, "coord": coord,
        "target_kind": "consistent",
        "fb_poly_degree": res["fb_poly_degree"], "n_fb_elements": res["n_fb_elements"],
        "system_nvars": res["nvars"],
        "solving_degree": d["d_reg"], "solving_degree_capped": d["reached_max"],
        "macaulay_bound": macaulay_bound,
        "gb_output_degree": gb_out_deg, "gb_basis_size": gb_basis,
        "gb_time_s": round(gb_time, 3),
        "macaulay_max_rows": d["max_matrix_rows"], "macaulay_max_cols": d["max_matrix_cols"],
        "quotient_dim": d["quotient_dim"], "min_gen_degree": d["min_gen_degree"],
        "gen_degrees": d["gen_degrees"], "n_lead_gens": d["n_lead_gens"],
        "n_confirmed_relations": res["n_confirmed"], "spurious": res["spurious"],
        "t_relations_s": round(res["t_build"], 4),
        "t_solve_s": round(res["t_solve"], 4),
        "t_linear_algebra_s": round(res["t_linalg"], 4),
        "t_ecverify_s": round(res["t_ecverify"], 4),
        "example_relation": res["example"],
        "per_degree": d["per_degree"],
    })
    return out


def prob_setting(bits, N, m, coord, T):
    """Relation measurement (no d_reg):
      * random targets R = k*G  -> the honest relation PROBABILITY (expected ~0 at toy
        sizes by the birthday law C(N,m)/(p/2); this is the P0 yield regime).
      * constructed targets R = sum_{i in S} +-P_i for random S -> nonzero RELATIONS FOUND
        by the system solver, every one EC-re-verified (spurious counted separately)."""
    C = find_toy_curve(bits, seed=SEED, require_cofactor_one=True)
    fb = build_glv_base(C, N) if coord == "invariant" else build_plain_base(C, N)
    rng = random.Random(2000 + bits * 11 + N * 3 + m + (0 if coord == "plain" else 1))
    confirmed = spurious = targets_with_rel = used = 0
    t_solve = t_build = t_ec = 0.0
    example = None
    for _ in range(T):
        k = rng.randrange(1, C.ell)
        R = ec_mul(k, C.gen, 0, C.p)
        if R is None:
            continue
        used += 1
        res = search_relations_system(C, fb, m, R, coord, measure_dreg=False)
        t_build += res["t_build"]; t_solve += res["t_solve"]; t_ec += res["t_ecverify"]
        nc = res["n_confirmed"]
        confirmed += nc
        spurious += res["spurious"]
        if nc:
            targets_with_rel += 1
        if example is None and res["example"] is not None:
            example = dict(res["example"]); example["k"] = k

    # constructed-target batch: guaranteed-decomposable targets to exercise "relations found"
    # (kept small for m>=3, whose per-target system solve is expensive)
    n_constructed = min(12 if m >= 3 else 30, len(fb.points))
    con_targets = con_recovered = con_spurious = 0
    for _ in range(n_constructed):
        idxs = rng.sample(range(len(fb.points)), m)
        R = None
        for i in idxs:
            P = fb.points[i]
            R = ec_add(R, P if rng.random() < 0.5 else (P[0], (-P[1]) % C.p), 0, C.p)
        if R is None:
            continue
        res = search_relations_system(C, fb, m, R, coord, measure_dreg=False)
        con_targets += 1
        con_spurious += res["spurious"]
        if frozenset(idxs) in {frozenset(t) for t in res["confirmed_relations"]}:
            con_recovered += 1
        if example is None and res["example"] is not None:
            example = dict(res["example"])

    out = dict(_curve_fields(C, N, fb))
    out.update({
        "block": "relation_probability", "m": m, "coord": coord,
        "trials": used,
        "confirmed_relations": confirmed, "spurious_solver_outputs": spurious,
        "targets_with_relation": targets_with_rel,
        "relation_probability": targets_with_rel / used if used else 0.0,
        "relations_per_target": confirmed / used if used else 0.0,
        "constructed_targets": con_targets,
        "constructed_recovered": con_recovered,
        "constructed_spurious": con_spurious,
        "t_relations_s": round(t_build, 3), "t_solve_s": round(t_solve, 3),
        "t_ecverify_s": round(t_ec, 3),
        "example_relation": example,
    })
    return out


# ------------------------------------------------------------------ grid
# Sizes are deliberately SMALL: this measures the REAL polynomial system (Groebner +
# graded Macaulay linear algebra), which is far more expensive than the univariate
# solves of P1/P1-m3. See RESULTS.md "what this does NOT establish / scale limits".

DREG_GRID = [
    # (bits, N, m, coord, dreg_max)
    # m=2 plain sweep -- solving degree grows ~2|F| (fully reached, capped=False):
    (16, 4, 2, "plain", 34), (16, 6, 2, "plain", 34), (16, 8, 2, "plain", 34),
    (16, 10, 2, "plain", 34), (16, 12, 2, "plain", 34),
    # p-independence of the solving degree (same |F|, larger prime):
    (20, 6, 2, "plain", 34), (20, 10, 2, "plain", 34),
    # m=2 invariant (coupled X,U; 2m=4 variables) -- feasible only at tiny sizes:
    (16, 3, 2, "invariant", 22), (16, 6, 2, "invariant", 22),
    # m=3 plain real system -- solving degree is near the Macaulay bound and the full
    # graded reduction is NOT reachable in pure Python; measured as a capped lower bound:
    (16, 5, 3, "plain", 15), (16, 6, 3, "plain", 15),
]

PROB_GRID = [
    # (bits, N, m, coord, T)
    (16, 8, 2, "plain", 120), (16, 12, 2, "plain", 120),
    (16, 12, 2, "invariant", 60),
    (16, 12, 3, "plain", 40),
]


def main(dreg_grid=None, prob_grid=None):
    dreg_grid = DREG_GRID if dreg_grid is None else dreg_grid
    prob_grid = PROB_GRID if prob_grid is None else prob_grid
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    measurements = []

    print("== degree-of-regularity block ==", flush=True)
    for bits, N, m, coord, dmax in dreg_grid:
        t0 = time.time()
        r = dreg_setting(bits, N, m, coord, dmax)
        measurements.append(r)
        print(f"[dreg {coord:9s} {bits}b m={m} N={N:2d}] "
              f"fbdeg={r['fb_poly_degree']:2d} nvars={r['system_nvars']} "
              f"solvedeg={r['solving_degree']}{'(capped)' if r['solving_degree_capped'] else ''} "
              f"(macaulay_bound={r['macaulay_bound']}, gb_out_deg={r['gb_output_degree']}) "
              f"macaulay={r['macaulay_max_rows']}x{r['macaulay_max_cols']} "
              f"quot={r['quotient_dim']} rels={r['n_confirmed_relations']} "
              f"spur={r['spurious']} | Trel={r['t_relations_s']}s Tsolve={r['t_solve_s']}s "
              f"Tlin={r['t_linear_algebra_s']}s (wall={time.time()-t0:.1f}s)", flush=True)

    print("== relation-probability block ==", flush=True)
    for bits, N, m, coord, T in prob_grid:
        t0 = time.time()
        r = prob_setting(bits, N, m, coord, T)
        measurements.append(r)
        print(f"[prob {coord:9s} {bits}b m={m} N={N:2d}] Trand={r['trials']} "
              f"relprob={r['relation_probability']:.3f} "
              f"conf_rand={r['confirmed_relations']} spur_rand={r['spurious_solver_outputs']} | "
              f"constructed={r['constructed_recovered']}/{r['constructed_targets']} recovered "
              f"spur={r['constructed_spurious']} (wall={time.time()-t0:.1f}s)", flush=True)

    man = p0manifest.Manifest(
        hypothesis="HYP_GLV_SEMAEV_001",
        variant="p3-sm-system",
        params={"seed": SEED,
                "dreg_grid": [list(x) for x in dreg_grid],
                "prob_grid": [list(x) for x in prob_grid],
                "method": "actual S_{m+1} relation SYSTEM {S_{m+1}=0, f_F(X_i)=0}; "
                          "lex-Groebner variety + graded Macaulay degree-of-regularity; "
                          "every relation EC-re-verified"},
        code_files=[str(_HERE / "semaev_system.py"),
                    str(_HERE / "run.py"),
                    str(_P1 / "semaev_solve.py"),
                    str(_P0 / "toy_curves.py")],
    )
    man.record({"measurements": measurements})
    path = man.write(timestamp)
    print(f"\nmanifest: {path}", flush=True)
    return measurements, path


if __name__ == "__main__":
    main()
