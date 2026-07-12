#!/usr/bin/env python3
"""P2 driver: MEASURE Ward-EDS rank-of-apparition and the torsion zero set across toy curves.

For each cofactor-1 toy curve ``E_b : y^2 = x^3 + b`` over ``p ≡ 1 (mod 3)`` (16/20/24-bit,
``find_toy_curve(bits, seed=1, require_cofactor_one=True)``) this measures, for the generator
``G`` and random points ``P = [s]G``:

  * the rank of apparition ``rho(P)`` = least ``n>0`` with ``W_n(P) ≡ 0 (mod p)``, and confirms
    ``rho(P) = ord(P)`` by INDEPENDENT ``ec_mul`` (compute ``[n]P`` and find its first hit of O);
  * the zero set ``{n : W_n ≡ 0, 1<=n<=N}`` and confirms it equals ``{multiples of ord}`` with
    every member re-verified by ``ec_mul``;
  * a broad ``(P, n)`` sample of the torsion equivalence ``W_n ≡ 0 ⟺ [n]P = O`` (via the
    O(log n) single-term EDS, so large ``n`` — including ``n = ell`` and ``2*ell`` — are cheap);
  * structural facts measured honestly: zeros form the arithmetic progression ``rho*Z`` (the
    zero-pattern period is ``rho``), Ward's master recurrence and the Somos-4 slice hold on the
    generated sequence, and (over Z, tiny cases) ``|W_n|`` growth for an infinite-order point.

Every run is recorded with the reused P0 ``manifest.py`` provenance helper.

HONESTY: this reports only measured numbers for the sizes actually run. It CONFIRMS the known
``psi_n`` torsion equivalence numerically; it makes NO asymptotic/complexity claim and NO claim
of any EDS-based ECDLP advantage. EDS re-encode point arithmetic; see RESULTS.md.
"""
from __future__ import annotations

import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_P0 = _HERE.parent / "p0_glv_semaev"
if str(_P0) not in sys.path:
    sys.path.insert(0, str(_P0))

import sympy  # noqa: E402
from toy_curves import find_toy_curve, ec_mul  # noqa: E402
import manifest as p0manifest  # noqa: E402

from eds import (  # noqa: E402
    eds_sequence, eds_term, zero_set, eds_sequence_Z,
    ward_master_holds, somos4_slice_holds,
)

# Retarget the reused manifest helper to THIS experiment's runs/ directory.
p0manifest.RUNS = _HERE / "runs"

SEED = 1

# Per-bit budget: zero-set scan bound (in units of ell), #random points given a FULL apparition
# scan, and #random points verified by the divisor argument (eds_term at n=ell, ell prime).
BUDGET = {
    16: {"zs_mult": 3, "n_full_scan_pts": 5, "n_div_pts": 20},
    20: {"zs_mult": 3, "n_full_scan_pts": 3, "n_div_pts": 20},
    24: {"zs_mult": 2, "n_full_scan_pts": 1, "n_div_pts": 20},  # scaled down: see RESULTS.md
}


def ec_order_first_hit(P, ell: int, a: int, p: int) -> int:
    """Independent ord(P): least n>0 with [n]P = O, using divisor structure of a prime ell.

    ord(P) divides #<G> = ell (prime), so ord in {1, ell}. Returns 1 if P=O, else ell if
    [ell]P=O. Fails loudly if [ell]P != O (would mean P not in <G>).
    """
    if P is None:
        return 1
    if ec_mul(ell, P, a, p) is not None:
        raise RuntimeError("point is not annihilated by ell; not in <G>")
    return ell


def measure_curve(bits: int) -> dict:
    t0 = time.time()
    C = find_toy_curve(bits, seed=SEED, require_cofactor_one=True)
    x, y = C.gen
    a, b, p, ell = 0, C.b, C.p, C.ell
    bud = BUDGET[bits]
    assert sympy.isprime(ell) and C.cofactor == 1 and C.order == ell

    # --- (A)+(B) one full sequence to N = zs_mult * ell; covers apparition + zero set. -------
    N = bud["zs_mult"] * ell
    W = eds_sequence(x, y, a, b, p, N)

    # (A) rank of apparition of G = least n>0 with W_n≡0.
    rho_G = next((n for n in range(1, N + 1) if W[n] % p == 0), None)
    ord_G_ec = ec_order_first_hit(C.gen, ell, a, p)   # independent
    apparition_match = (rho_G == ord_G_ec == ell)

    # (B) zero set == multiples of ord(G), each member re-verified by ec_mul.
    zs = zero_set(W, p)
    multiples = list(range(ell, N + 1, ell))
    zeroset_eq_multiples = (zs == multiples)
    zeros_ec_confirmed = all(ec_mul(n, C.gen, a, p) is None for n in zs)
    # spot-check a sample of NON-zero indices really give [n]G != O.
    rng = random.Random(4242 + bits)
    nonzero_sample = [rng.randrange(1, N + 1) for _ in range(200)]
    nonzero_sample = [n for n in nonzero_sample if n % ell != 0]
    nonzeros_ec_confirmed = all(
        (W[n] % p != 0) and (ec_mul(n, C.gen, a, p) is not None) for n in nonzero_sample
    )

    # --- (C) random-point apparition: FULL scan on a few points (confirms zeros = AP rho*Z). --
    full_scan_pts = []
    for _ in range(bud["n_full_scan_pts"]):
        s = rng.randrange(1, ell)
        P = ec_mul(s, C.gen, a, p)
        px, py = P
        WP = eds_sequence(px, py, a, b, p, ell)
        rho_P = next((n for n in range(1, ell + 1) if WP[n] % p == 0), None)
        ordP = ec_order_first_hit(P, ell, a, p)
        # verify the FULL zero-set of P inside [1, ell] is exactly {ell} (prime order).
        zeros_P = [n for n in range(1, ell + 1) if WP[n] % p == 0]
        full_scan_pts.append({
            "s": s, "rho_P": rho_P, "ord_P_ec": ordP,
            "match": (rho_P == ordP == ell), "zeros_in_1_ell": zeros_P,
        })

    # --- (C') random-point apparition by DIVISOR argument (cheap, uses eds_term at n=ell). ----
    div_pts = []
    for _ in range(bud["n_div_pts"]):
        s = rng.randrange(1, ell)
        P = ec_mul(s, C.gen, a, p)
        px, py = P
        w_ell = eds_term(px, py, a, b, p, ell) % p
        w1 = eds_term(px, py, a, b, p, 1) % p          # == 1
        ordP = ec_order_first_hit(P, ell, a, p)
        # rho | ord = ell (prime); W_1 != 0 rules out rho=1; W_ell = 0 gives rho = ell.
        rho_P = ell if (w_ell == 0 and w1 != 0) else None
        div_pts.append({"s": s, "w_ell_is_zero": w_ell == 0, "rho_P": rho_P,
                        "ord_P_ec": ordP, "match": (rho_P == ordP == ell)})

    # --- (D) broad (P,n) torsion equivalence sample: W_n≡0 ⟺ [n]P=O, via O(log n) eds_term. --
    pn_samples = 0
    pn_zero_cases = 0     # cases where BOTH sides are zero (the informative direction)
    pn_mismatch = 0
    example_zero = None
    for _ in range(400):
        s = rng.randrange(1, ell)
        P = ec_mul(s, C.gen, a, p)
        px, py = P
        # mix: small n, n near ell, and exact multiples of ell (forced zero cases).
        choice = rng.random()
        if choice < 0.34:
            n = rng.randrange(1, 5000)
        elif choice < 0.67:
            n = rng.randrange(ell - 50, ell + 50)
        else:
            n = ell * rng.randrange(1, 4)
        eds_zero = (eds_term(px, py, a, b, p, n) % p == 0)
        ec_zero = (ec_mul(n, P, a, p) is None)
        pn_samples += 1
        if eds_zero != ec_zero:
            pn_mismatch += 1
        if eds_zero and ec_zero:
            pn_zero_cases += 1
            if example_zero is None:
                example_zero = {"s": s, "P": [px, py], "n": n}

    # --- (E) recurrence cross-checks on the generated sequence. ------------------------------
    ward_ok = 0
    for _ in range(1000):
        m = rng.randrange(2, min(N, 20000) - 2)
        n = rng.randrange(1, m + 1)
        if m + n <= N and m - n >= 1:
            assert ward_master_holds(W, p, m, n)
            ward_ok += 1
    somos_ok = 0
    for _ in range(1000):
        m = rng.randrange(2, min(N, 20000) - 2)
        assert somos4_slice_holds(W, p, m, b, y)
        somos_ok += 1

    # --- (F) zero-pattern period is rho (zeros = AP). Value-period: scan a modest bound. -----
    #     (Cheap check only on 16-bit; on larger curves it is left "not determined".)
    value_period_bound = None
    value_period_found = None
    if bits == 16:
        Kscan = 30
        Wv = eds_sequence(x, y, a, b, p, Kscan * ell + 64)
        value_period_bound = Kscan * ell
        for k in range(1, Kscan + 1):
            T = k * ell
            if all(Wv[i + T] == Wv[i] for i in range(0, 48)):
                value_period_found = T
                break

    dt = time.time() - t0
    return {
        "bits": bits,
        "p": p, "b": b, "order": C.order, "ell": ell, "cofactor": C.cofactor,
        "generator": [x, y], "beta": C.beta, "lambda": C.lam,
        # keys below let validate_run.validate_measurement re-audit the curve/GLV data:
        "base_size": 0,
        # --- (A) apparition of G ---
        "N_zeroset": N,
        "rho_G_eds": rho_G, "ord_G_ec": ord_G_ec, "apparition_match": apparition_match,
        # --- (B) zero set ---
        "zero_set": zs, "multiples_of_ord": multiples,
        "zeroset_eq_multiples": zeroset_eq_multiples,
        "zeros_ec_confirmed": zeros_ec_confirmed,
        "nonzero_sample_size": len(nonzero_sample),
        "nonzeros_ec_confirmed": nonzeros_ec_confirmed,
        # --- (C) random points ---
        "full_scan_points": full_scan_pts,
        "full_scan_all_match": all(q["match"] for q in full_scan_pts),
        "divisor_points": div_pts,
        "divisor_all_match": all(q["match"] for q in div_pts),
        # --- (D) (P,n) torsion equivalence ---
        "pn_samples": pn_samples, "pn_zero_cases": pn_zero_cases,
        "pn_mismatch": pn_mismatch, "pn_example_zero": example_zero,
        # --- (E) recurrence cross-checks ---
        "ward_master_checks": ward_ok, "somos4_slice_checks": somos_ok,
        # --- (F) periodicity ---
        "zero_pattern_period": ell,
        "value_period_scan_bound": value_period_bound,
        "value_period_found": value_period_found,
        "wall_time_s": round(dt, 3),
    }


def growth_demo() -> dict:
    """Integer EDS: |W_n| growth for an infinite-order point, and a torsion apparition over Z."""
    inf_pt = eds_sequence_Z(3, 5, 0, -2, 10)   # (3,5) on y^2 = x^3 - 2, infinite order
    tors_pt = eds_sequence_Z(2, 3, 0, 1, 12)   # (2,3) on y^2 = x^3 + 1, order 6
    return {
        "infinite_order": {
            "curve": "y^2 = x^3 - 2", "point": [3, 5],
            "W_1_to_10": inf_pt[1:11],
            "digit_lengths": [len(str(abs(w))) for w in inf_pt[1:11]],
            "any_zero_in_1_10": any(w == 0 for w in inf_pt[1:11]),
        },
        "torsion_order6": {
            "curve": "y^2 = x^3 + 1", "point": [2, 3],
            "W_0_to_12": tors_pt,
            "apparition_Z": next(n for n in range(1, 13) if tors_pt[n] == 0),
        },
    }


def main():
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    measurements = []
    for bits in (16, 20, 24):
        m = measure_curve(bits)
        measurements.append(m)
        print(f"[{bits:2d}b p={m['p']:>10} ell={m['ell']:>10}] "
              f"rho(G)={m['rho_G_eds']} ord(G)={m['ord_G_ec']} "
              f"appar_match={m['apparition_match']} | "
              f"zeroset={m['zero_set']} ==multiples? {m['zeroset_eq_multiples']} "
              f"(ec_ok={m['zeros_ec_confirmed']}) | "
              f"fullscanPts={len(m['full_scan_points'])} match={m['full_scan_all_match']} "
              f"divPts={len(m['divisor_points'])} match={m['divisor_all_match']} | "
              f"(P,n) samples={m['pn_samples']} zeroCases={m['pn_zero_cases']} "
              f"mismatch={m['pn_mismatch']} | ward={m['ward_master_checks']} "
              f"somos={m['somos4_slice_checks']} | {m['wall_time_s']}s")

    growth = growth_demo()
    print(f"[growth] infinite-order (3,5)/y^2=x^3-2 digit-lengths W_1..10="
          f"{growth['infinite_order']['digit_lengths']} "
          f"(no zeros? {not growth['infinite_order']['any_zero_in_1_10']}); "
          f"torsion (2,3)/y^2=x^3+1 apparition_Z={growth['torsion_order6']['apparition_Z']}")

    man = p0manifest.Manifest(
        hypothesis="HYP_WARD_EDS_001",
        variant="p2-ward-eds",
        params={"seed": SEED, "bits": [16, 20, 24], "budget": BUDGET,
                "method": "Ward normalized EDS via closed forms W0..W4 + doubling recurrence, "
                          "mod p; torsion re-verified by independent ec_mul"},
        code_files=[str(_HERE / "eds.py"),
                    str(_HERE / "run.py"),
                    str(_P0 / "toy_curves.py")],
    )
    man.record({"measurements": measurements, "growth_demo": growth})
    path = man.write(timestamp)
    print(f"\nmanifest: {path}")
    return measurements, path


if __name__ == "__main__":
    main()
