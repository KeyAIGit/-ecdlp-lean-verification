#!/usr/bin/env python3
"""P4 driver: build and Groebner-solve the COMPOSED low-degree map Semaev relation
SYSTEM, measure its degree of regularity / Macaulay matrices, and DIRECTLY compare to
the P3 RAW baseline (2|F|+1) at matched effective |F| -- on the SAME factor base.

For each (map kind, size) the DEGREE-OF-REGULARITY block:
  * builds the composed-map factor base (real on-curve EC points),
  * on ONE representative consistent target R = P_a + P_b (a relation is present):
      - solves the composed-map relation system and measures its d_reg / Macaulay matrix
        with the P3 graded-Macaulay engine,
      - ALSO measures the RAW P3 baseline system {S3=0, f_F(X_i)=0} d_reg on the SAME
        |F| factor base, so each row carries the composed-vs-raw comparison,
  * records relations found + spurious (EC-re-verified).

The RELATION block draws constructed + random targets and counts EC-confirmed relations
and (separately) spurious solver outputs, for both composed and raw systems.

HONESTY (see RESULTS.md): measured-only; DESCRIPTIVE-ONLY; no asymptotic/advantage/no-go
claim. The composed map is an HONEST APPROXIMATION to Petit (prime-field, no Weil
descent) -- stated in semaev_petit.py and RESULTS.md. Every relation is EC-re-verified;
the independent gate is validate.py (brute-force EC, no solver imports). Provenance via
the P0 manifest helper.
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
_P3 = _HERE.parent / "p3_sm_system"
for _d in (_P0, _P1, _P3):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))

from toy_curves import find_toy_curve, ec_add, ec_mul  # noqa: E402
import manifest as p0manifest  # noqa: E402

from semaev_petit import (make_map, build_petit_base, search_relations_petit,  # noqa: E402
                          build_product_system, build_single_aux_system,
                          build_raw_baseline_system)
from semaev_system import grevlex_gb_max_degree  # noqa: E402

p0manifest.RUNS = _HERE / "runs"
SEED = 1


def _curve_fields(C, base):
    return {
        "bits": C.bits, "p": C.p, "b": C.b, "order": C.order, "ell": C.ell,
        "cofactor": C.cofactor, "generator": list(C.gen), "beta": C.beta,
        "lambda": C.lam, "sqrt_p": isqrt(C.p),
        "n_distinct_x": base.n_distinct_x, "n_image_total": base.n_image_total,
        "aux_domain_size": base.aux_domain_size,
    }


def _consistent_target(C, base, m):
    R = None
    for idx in range(m):
        R = ec_add(R, base.points[idx], 0, C.p)
    return R


def _mapspec_dict(mp):
    d = {"kind": mp.kind, "describe": mp.describe()}
    if mp.kind == "product_2aux":
        d.update({"b0": mp.b0, "kappa": mp.kappa, "c": mp.c})
    else:
        d.update({"nt": mp.nt, "a1": mp.a1, "a2": mp.a2, "a3": mp.a3})
    return d


def dreg_setting(bits, kind, size, m, dreg_max, raw_dreg_max):
    """One degree-of-regularity measurement: composed map system AND the raw P3 baseline,
    on the SAME on-curve factor base, at a representative consistent target."""
    C = find_toy_curve(bits, seed=SEED, require_cofactor_one=True)
    mp = make_map(C, kind, size)
    base = build_petit_base(C, mp)
    R = _consistent_target(C, base, m)

    comp = search_relations_petit(C, base, m, R, kind, measure_dreg=True, dreg_max=dreg_max)
    raw = search_relations_petit(C, base, m, R, "raw_baseline",
                                 measure_dreg=True, dreg_max=raw_dreg_max)
    dc, dr = comp["d_reg"], raw["d_reg"]

    # complementary reduced-grevlex GB output degree for the composed system (small; NOT
    # the solving degree -- reported to keep the P3 distinction explicit).
    if kind == "product_2aux":
        sysb = build_product_system(m, mp, R[0], C.b, C.p)
    else:
        sysb = build_single_aux_system(m, mp, R[0], C.b, C.p)
    gb_out_deg, gb_basis, gb_time = grevlex_gb_max_degree(sysb.gens, sysb.solve_vars, C.p)

    comp_bound = sum(dc["gen_degrees"]) - comp["nvars"] + 1
    F = base.n_distinct_x
    out = dict(_curve_fields(C, base))
    out.update({
        "block": "degree_of_regularity", "m": m, "variant": kind,
        "map": _mapspec_dict(mp),
        "n_fb_elements": F, "raw_baseline_2F_plus_1": 2 * F + 1,
        # composed system
        "composed_nvars": comp["nvars"],
        "composed_fb_poly_degree": comp["fb_poly_degree"],
        "composed_solving_degree": dc["d_reg"],
        "composed_solving_degree_capped": dc["reached_max"],
        "composed_macaulay_bound": comp_bound,
        "composed_macaulay_max_rows": dc["max_matrix_rows"],
        "composed_macaulay_max_cols": dc["max_matrix_cols"],
        "composed_quotient_dim": dc["quotient_dim"],
        "composed_gen_degrees": dc["gen_degrees"],
        "gb_output_degree": gb_out_deg, "gb_basis_size": gb_basis,
        "gb_time_s": round(gb_time, 3),
        # raw P3 baseline on the SAME |F|
        "raw_nvars": raw["nvars"],
        "raw_fb_poly_degree": raw["fb_poly_degree"],
        "raw_solving_degree": dr["d_reg"],
        "raw_solving_degree_capped": dr["reached_max"],
        "raw_macaulay_max_rows": dr["max_matrix_rows"],
        "raw_macaulay_max_cols": dr["max_matrix_cols"],
        # relations / timing
        "composed_confirmed_relations": comp["n_confirmed"], "composed_spurious": comp["spurious"],
        "raw_confirmed_relations": raw["n_confirmed"], "raw_spurious": raw["spurious"],
        "composed_t_build_s": round(comp["t_build"], 4),
        "composed_t_solve_s": round(comp["t_solve"], 4),
        "composed_t_linalg_s": round(comp["t_linalg"], 4),
        "raw_t_linalg_s": round(raw["t_linalg"], 4),
        "composed_example": comp["example"], "raw_example": raw["example"],
        "composed_per_degree": dc["per_degree"],
    })
    return out


def relation_setting(bits, kind, size, m, T):
    """Relations found + spurious on constructed and random targets, composed vs raw."""
    C = find_toy_curve(bits, seed=SEED, require_cofactor_one=True)
    mp = make_map(C, kind, size)
    base = build_petit_base(C, mp)
    rng = random.Random(9000 + bits + size + m + (0 if kind == "product_2aux" else 1))

    def _batch(variant, targets):
        conf = spur = twr = 0
        ex = None
        for R in targets:
            res = search_relations_petit(C, base, m, R, variant, measure_dreg=False)
            conf += res["n_confirmed"]; spur += res["spurious"]
            if res["n_confirmed"]:
                twr += 1
            if ex is None and res["example"] is not None:
                ex = res["example"]
        return conf, spur, twr, ex

    # random targets R = k*G
    rand_targets = []
    for _ in range(T):
        R = ec_mul(rng.randrange(1, C.ell), C.gen, 0, C.p)
        if R is not None:
            rand_targets.append(R)
    # constructed targets R = e_i P_i + e_j P_j (guaranteed decomposable)
    con_specs = []
    for _ in range(min(20, len(base.points) * (len(base.points) - 1) // 2)):
        idxs = rng.sample(range(len(base.points)), m)
        R = None
        for i in idxs:
            P = base.points[i]
            R = ec_add(R, P if rng.random() < 0.5 else (P[0], (-P[1]) % C.p), 0, C.p)
        if R is not None:
            con_specs.append((frozenset(idxs), R))

    c_conf, c_spur, c_twr, c_ex = _batch(kind, rand_targets)
    r_conf, r_spur, r_twr, r_ex = _batch("raw_baseline", rand_targets)
    # constructed recovery for the composed system
    con_recovered = con_targets = con_spur = 0
    for want, R in con_specs:
        res = search_relations_petit(C, base, m, R, kind, measure_dreg=False)
        con_targets += 1; con_spur += res["spurious"]
        if want in {frozenset(t) for t in res["confirmed_relations"]}:
            con_recovered += 1

    out = dict(_curve_fields(C, base))
    out.update({
        "block": "relations", "m": m, "variant": kind, "map": _mapspec_dict(mp),
        "n_fb_elements": base.n_distinct_x,
        "random_trials": len(rand_targets),
        "composed_random_confirmed": c_conf, "composed_random_spurious": c_spur,
        "composed_random_targets_with_rel": c_twr,
        "raw_random_confirmed": r_conf, "raw_random_spurious": r_spur,
        "raw_random_targets_with_rel": r_twr,
        "relation_probability": c_twr / len(rand_targets) if rand_targets else 0.0,
        "constructed_targets": con_targets, "constructed_recovered": con_recovered,
        "constructed_spurious": con_spur,
        "composed_example": c_ex, "raw_example": r_ex,
    })
    return out


# ------------------------------------------------------------------ grids
# SMALL by necessity: the composed systems live in 3m variables (vs P3's m or 2m), so the
# pure-Python graded Macaulay engine grows fast. See RESULTS.md scale limits.

DREG_GRID = [
    # (bits, kind, size, m, dreg_max, raw_dreg_max)
    # product_2aux: |F| ~ b0^2, defining degree ~ b0 ~ sqrt(|F|). This is the
    # degree-REDUCING candidate. 3m=6 variables -> the graded Macaulay engine is far
    # heavier than P3's m-variable raw baseline; the cap keeps it finite.
    (16, "product_2aux", 2, 2, 9, 20),      # |F| ~ 4 (terminates at D=9)
    # single_aux_composed: |F| ~ nt, defining degree RELOCATED to g(t) of degree nt (NOT
    # reduced). Also 6 variables; capped lower bound where termination is not reached:
    (16, "single_aux_composed", 4, 2, 9, 20),
]

REL_GRID = [
    # (bits, kind, size, m, T)  -- relation block skips d_reg (fast variety solves only),
    # so it runs at LARGER |F| to exercise relations-found + spurious at bigger factor bases.
    (16, "product_2aux", 3, 2, 40),           # |F| ~ 9
    (16, "single_aux_composed", 6, 2, 40),    # |F| ~ 6
]


def main(dreg_grid=None, rel_grid=None):
    dreg_grid = DREG_GRID if dreg_grid is None else dreg_grid
    rel_grid = REL_GRID if rel_grid is None else rel_grid
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    measurements = []

    print("== degree-of-regularity block (composed map vs raw P3 baseline) ==", flush=True)
    for bits, kind, size, m, dmax, rdmax in dreg_grid:
        t0 = time.time()
        r = dreg_setting(bits, kind, size, m, dmax, rdmax)
        measurements.append(r)
        print(f"[dreg {kind:20s} {bits}b size={size} m={m}] |F|={r['n_fb_elements']:2d} "
              f"COMPOSED nvars={r['composed_nvars']} d_reg="
              f"{r['composed_solving_degree']}{'(cap)' if r['composed_solving_degree_capped'] else ''} "
              f"mac={r['composed_macaulay_max_rows']}x{r['composed_macaulay_max_cols']} "
              f"quot={r['composed_quotient_dim']} | "
              f"RAW d_reg={r['raw_solving_degree']}{'(cap)' if r['raw_solving_degree_capped'] else ''} "
              f"(2|F|+1={r['raw_baseline_2F_plus_1']}) "
              f"mac={r['raw_macaulay_max_rows']}x{r['raw_macaulay_max_cols']} | "
              f"rels={r['composed_confirmed_relations']} spur={r['composed_spurious']} "
              f"Tlin_c={r['composed_t_linalg_s']}s Tlin_r={r['raw_t_linalg_s']}s "
              f"(wall={time.time()-t0:.1f}s)", flush=True)

    print("== relation block ==", flush=True)
    for bits, kind, size, m, T in rel_grid:
        t0 = time.time()
        r = relation_setting(bits, kind, size, m, T)
        measurements.append(r)
        print(f"[rel  {kind:20s} {bits}b size={size} m={m}] |F|={r['n_fb_elements']:2d} "
              f"Trand={r['random_trials']} relprob={r['relation_probability']:.3f} "
              f"comp_rand_conf={r['composed_random_confirmed']} spur={r['composed_random_spurious']} | "
              f"constructed={r['constructed_recovered']}/{r['constructed_targets']} "
              f"spur={r['constructed_spurious']} (wall={time.time()-t0:.1f}s)", flush=True)

    man = p0manifest.Manifest(
        hypothesis="HYP_GLV_SEMAEV_001",
        variant="p4-petit-factorbase",
        params={"seed": SEED,
                "dreg_grid": [list(x) for x in dreg_grid],
                "rel_grid": [list(x) for x in rel_grid],
                "method": "composed low-degree map factor base {S_{m+1}=0, X_i=phi(aux), "
                          "g(aux)=0} vs raw P3 baseline {S_{m+1}=0, f_F(X_i)=0}; lex-Groebner "
                          "variety + graded Macaulay degree-of-regularity; every relation "
                          "EC-re-verified. HONEST APPROXIMATION to Petit (prime field, no Weil "
                          "descent)."},
        code_files=[str(_HERE / "semaev_petit.py"),
                    str(_HERE / "run.py"),
                    str(_P3 / "semaev_system.py"),
                    str(_P1 / "semaev_solve.py"),
                    str(_P0 / "toy_curves.py")],
    )
    man.record({"measurements": measurements})
    path = man.write(timestamp)
    print(f"\nmanifest: {path}", flush=True)
    return measurements, path


if __name__ == "__main__":
    main()
