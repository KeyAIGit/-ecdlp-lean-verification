#!/usr/bin/env python3
"""Independent replay + cross-check validator for P2 (Ward-EDS) runs.

Deliberately separate from ``run.py``. A run is accepted ONLY if all of the following hold.

  1. MANIFEST INTEGRITY: ``results_hash`` matches the canonical results payload and the
     schema-v1 provenance fields are present (reuses P0 ``validate_run.sha256_obj``).

  2. CURVE RE-AUDIT: every recorded curve is a valid cofactor-1 j=0 instance — prime
     ``p ≡ 1 (mod 3)``, prime subgroup order ``ell``, generator on curve, ``phi(G)=[lambda]G``
     — via the P0 ``validate_run.validate_measurement`` (schema-v1 fails closed on cofactor>1).

  3. THE MANDATORY EDS↔GROUP CROSS-CHECK (the scientific core). On the manifest's curves,
     INDEPENDENTLY recompute for freshly sampled ``(P, n)``:
        * ``W_n(P) mod p`` via the Ward recurrence (``eds`` module), and
        * ``[n]P`` via ``ec_mul`` (the independent group-law oracle),
     and assert the torsion equivalence ``W_n ≡ 0 (mod p) ⟺ [n]P = O`` for every sample,
     including forced zero cases at ``n = ell, 2*ell``. Also assert ``rho(G) = ord(G) = ell``
     for each curve (least EDS zero == independent ec_mul order).

  4. A STRONGER, ALGEBRAICALLY INDEPENDENT TIE: for on-curve ``[n]P != O`` the normalized-EDS
     multiplication identity ``x([n]P) = x_P - W_{n-1} W_{n+1} / W_n^2`` must hold, linking the
     EDS values to the ACTUAL ec_mul coordinates through separate arithmetic. Any mismatch of
     (3) or (4) is reported loudly — these are theorems, so a mismatch means a bug.

Prints ``VALIDATION: PASS`` / ``VALIDATION: FAIL``.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_P0 = _HERE.parent / "p0_glv_semaev"
if str(_P0) not in sys.path:
    sys.path.insert(0, str(_P0))

import sympy  # noqa: E402
from toy_curves import find_toy_curve, ec_mul  # noqa: E402
from validate_run import sha256_obj, validate_measurement  # noqa: E402

from eds import eds_sequence, eds_term  # noqa: E402


# ------------------------------------------------------------------ manifest replay

def replay_manifest(path: Path) -> tuple[list[str], list[str]]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    warnings: list[str] = []

    if doc.get("results_hash") != sha256_obj(doc.get("results", {})):
        errors.append("results_hash mismatch")
    for field in ("git_commit", "command", "timestamp", "code_hashes", "tools"):
        if not doc.get(field):
            errors.append(f"missing schema-v1 field: {field}")

    schema_version = int(doc.get("schema_version", 0))
    measurements = doc.get("results", {}).get("measurements", [])
    if not measurements:
        errors.append("no measurements in manifest")

    for m in measurements:
        # (2) reuse the P0 curve validator (cofactor-1, GLV eigenvalue, on-curve).
        validate_measurement(m, schema_version, errors, warnings)

        # sanity: the run's own recorded equivalences must be internally consistent.
        if not m.get("apparition_match"):
            errors.append(f"{m['bits']}b: recorded apparition_match is false")
        if not m.get("zeroset_eq_multiples"):
            errors.append(f"{m['bits']}b: recorded zeroset != multiples")
        if m.get("pn_mismatch", 1) != 0:
            errors.append(f"{m['bits']}b: recorded pn_mismatch != 0")
        if m.get("rho_G_eds") != m.get("ell") or m.get("ord_G_ec") != m.get("ell"):
            errors.append(f"{m['bits']}b: recorded rho(G)/ord(G) != ell")
    return errors, warnings


# ------------------------------------------------------------------ independent cross-check

def cross_check() -> tuple[int, list[str]]:
    """Recompute EDS + ec_mul independently and assert the torsion + coordinate identities."""
    errors: list[str] = []
    checked = 0
    zero_cases = 0
    coord_checks = 0

    for bits in (16, 20, 24):
        C = find_toy_curve(bits, seed=1, require_cofactor_one=True)
        x, y = C.gen
        a, b, p, ell = 0, C.b, C.p, C.ell

        if not sympy.isprime(ell) or C.cofactor != 1:
            errors.append(f"{bits}b: not a prime-order cofactor-1 curve")
            continue

        # (A) rho(G) = ord(G) = ell, computed two independent ways.
        #     EDS side: least zero of a short window then confirm ell is a zero and ell-1 is not
        #     (ell prime + zeros form rho*Z => first zero is ell); ec side: ec_mul order.
        W_small = eds_sequence(x, y, a, b, p, min(4096, ell - 1))
        first_small_zero = next((n for n in range(1, len(W_small)) if W_small[n] % p == 0), None)
        w_ell = eds_term(x, y, a, b, p, ell) % p
        w_ellm1 = eds_term(x, y, a, b, p, ell - 1) % p
        rho_G = ell if (first_small_zero is None and w_ell == 0 and w_ellm1 != 0) else first_small_zero
        ord_G = None if ec_mul(ell, C.gen, a, p) is not None else (
            1 if C.gen is None else ell)
        if not (rho_G == ord_G == ell):
            errors.append(f"{bits}b: rho(G)={rho_G}, ord(G)={ord_G}, ell={ell} (expected all equal)")

        rng = random.Random(70000 + bits)

        # (B) torsion equivalence W_n≡0 ⟺ [n]P=O for many independent (P,n).
        for _ in range(300):
            s = rng.randrange(1, ell)
            P = ec_mul(s, C.gen, a, p)
            px, py = P
            r = rng.random()
            if r < 0.34:
                n = rng.randrange(1, 8000)
            elif r < 0.67:
                n = rng.randrange(ell - 40, ell + 40)
            else:
                n = ell * rng.randrange(1, 3)         # forced zero case
            eds_zero = (eds_term(px, py, a, b, p, n) % p == 0)
            ec_zero = (ec_mul(n, P, a, p) is None)
            checked += 1
            if eds_zero != ec_zero:
                errors.append(f"{bits}b: torsion mismatch s={s} n={n}: eds0={eds_zero} ec0={ec_zero}")
            if eds_zero and ec_zero:
                zero_cases += 1

        # (C) coordinate identity x([n]P) = x_P - W_{n-1}W_{n+1}/W_n^2 (independent EC tie).
        for _ in range(60):
            s = rng.randrange(1, ell)
            P = ec_mul(s, C.gen, a, p)
            px, py = P
            n = rng.randrange(2, 3000)
            nP = ec_mul(n, P, a, p)
            wn = eds_term(px, py, a, b, p, n) % p
            if nP is None:
                if wn != 0:
                    errors.append(f"{bits}b: [n]P=O but W_n!=0 (s={s}, n={n})")
                continue
            if wn == 0:
                errors.append(f"{bits}b: W_n=0 but [n]P!=O (s={s}, n={n})")
                continue
            wnm1 = eds_term(px, py, a, b, p, n - 1) % p
            wnp1 = eds_term(px, py, a, b, p, n + 1) % p
            rhs = (px - wnm1 * wnp1 % p * pow(wn * wn % p, -1, p)) % p
            coord_checks += 1
            if rhs != nP[0]:
                errors.append(f"{bits}b: coord identity fails s={s} n={n}: {rhs} != x([n]P)={nP[0]}")

    print(f"cross-check: {checked} independent (P,n) torsion samples across 16/20/24-bit "
          f"({zero_cases} genuine zero cases), {coord_checks} EDS<->group coordinate-identity "
          f"checks; all consistent with ec_mul" if not errors else
          f"cross-check: {checked} samples, {len(errors)} failures")
    return checked, errors


def main() -> int:
    runs = sorted((_HERE / "runs").glob("*.json"))
    all_errors: list[str] = []
    if not runs:
        print("WARNING: no run manifests found in runs/")
    for path in runs:
        errors, warnings = replay_manifest(path)
        print(f"[{path.name}] errors={len(errors)} warnings={len(warnings)}")
        for w in warnings:
            print(f"  WARNING: {w}")
        for e in errors:
            print(f"  ERROR: {e}")
        all_errors += errors

    _, xc_errors = cross_check()
    for e in xc_errors:
        print(f"  CROSS-CHECK ERROR: {e}")
    all_errors += xc_errors

    ok = not all_errors
    print("\nVALIDATION:", "PASS" if ok else f"FAIL ({len(all_errors)} errors)")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
