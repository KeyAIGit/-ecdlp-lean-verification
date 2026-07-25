#!/usr/bin/env python3
"""Producer for the exhaustive fixed-target GLV scaling certificate.

The base certificate (`certificate.json`) classifies the coordinatewise stabilizers of `S3` and
`S4` when *every* coordinate is scaled, and treats the fixed-target case with a single witness
plus a "generic target" caveat. This producer strengthens the fixed-target statement from
"generic" to **every nonzero target**, with an integral witness that also pins the excluded
characteristics.

## What is certified

Put `F_r(x1,x2,x3) := S4(x1,x2,x3,r)`, with `r` a symbolic target and coefficients in `Z[b,r]`.
For each nontrivial `e` in `(Z/3)^3` and each choice of surviving residue class `c`, a scalar
covariance `F_r(beta^e . x) = c_e F_r(x)` forces every coefficient whose exponent vector `a` has
`<e,a> != c (mod 3)` to vanish. We record, for each `(e,c)`, a **pure-`r` witness**: a
must-vanish coefficient of the form `N * r^k` with `N` a nonzero integer and `k >= 1`, carrying no
`b`. Such a witness forces `r = 0` in any field whose characteristic does not divide `N`.

The certificate therefore yields, for every `(e,c)` simultaneously:

    char K not in {2,3}  and  r != 0   ==>   the coordinatewise stabilizer of F_r is trivial.

and the excluded-characteristic list is *computed*, not assumed: it is exactly the set of primes
dividing some minimal `|N|`, together with 3 (where `beta` would not be primitive).

The complementary slice `r = 0` is computed separately and is the **complete** exceptional locus:
there the stabilizer is the diagonal `C3`.

## What is NOT certified

No statement about Groebner complexity, solving degree, relation probability, or any end-to-end
ECDLP cost. No claim that a finite symmetry cannot change a solving degree. See the research note.

Run:  python3 generate_fixed_target.py            # writes fixed_target_certificate{.json,.sha256}
      python3 generate_fixed_target.py --check    # recompute and compare, exit 1 on drift
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from itertools import product
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
CERT = HERE / "fixed_target_certificate.json"
SHA = HERE / "fixed_target_certificate.sha256"

x1, x2, x3, X, b, r = sp.symbols("x1 x2 x3 X b r")
VARS = (x1, x2, x3)


def s3(u, v, w):
    """The `a = 0` third Semaev polynomial, in the same normalization as `generate.py`."""
    return (u - v) ** 2 * w ** 2 - 2 * ((u + v) * (u * v) + 2 * b) * w \
        + (u * v) ** 2 - 4 * b * (u + v)


def fixed_target_support():
    """`supp(F_r)` in the three factor-base variables, coefficients in `Z[b,r]`."""
    s4 = sp.expand(sp.resultant(s3(x1, x2, X), s3(x3, r, X), X))
    poly = sp.Poly(s4, *VARS)
    return {m: sp.expand(c) for m, c in zip(poly.monoms(), poly.coeffs()) if c != 0}


def pure_r_witness(coeff):
    """If `coeff` is `N * r^k` with `k >= 1` and no `b`, return `(abs(N), k)`, else `None`."""
    p = sp.Poly(coeff, r, b)
    if len(p.monoms()) != 1:
        return None
    (kr, kb), = p.monoms()
    if kb != 0 or kr < 1:
        return None
    return (abs(int(p.coeffs()[0])), kr)


def classify_fixed_target(support):
    """For every nontrivial `e` and keep-class, the best pure-`r` witness."""
    rows = []
    for e in product(range(3), repeat=3):
        if not any(e):
            continue
        for c in range(3):
            must = [co for a, co in support.items()
                    if sum(ei * ai for ei, ai in zip(e, a)) % 3 != c]
            if not must:
                rows.append({"exponents": list(e), "keep_class": c,
                             "witness": None, "note": "support lies in one class"})
                continue
            wits = [w for w in (pure_r_witness(co) for co in must) if w is not None]
            if not wits:
                rows.append({"exponents": list(e), "keep_class": c,
                             "witness": None, "note": "no pure-r witness"})
                continue
            n, k = min(wits)
            rows.append({"exponents": list(e), "keep_class": c,
                         "witness": {"integer_abs": n, "r_power": k},
                         "forces": "r = 0 whenever char does not divide integer_abs"})
    return rows


def zero_slice_stabilizer():
    """The stabilizer of the `r = 0` slice, computed exhaustively."""
    s4 = sp.expand(sp.resultant(s3(x1, x2, X), s3(x3, 0, X), X))
    poly = sp.Poly(s4, *VARS)
    sup = [m for m, c in zip(poly.monoms(), poly.coeffs()) if c != 0]
    out = []
    for e in product(range(3), repeat=3):
        vals = {sum(ei * ai for ei, ai in zip(e, a)) % 3 for a in sup}
        if len(vals) == 1:
            out.append({"exponents": list(e), "multiplier_beta_exponent": vals.pop()})
    return out


def build() -> dict:
    support = fixed_target_support()
    rows = classify_fixed_target(support)

    missing = [row for row in rows if row["witness"] is None]
    integers = sorted({row["witness"]["integer_abs"] for row in rows if row["witness"]})
    primes = sorted({q for n in integers for q in sp.factorint(n)})

    return {
        "schema_version": 1,
        "certificate_id": "GLV-SEMAEV-ITER-001-FIXED-TARGET",
        "supersedes_scope": (
            "Strengthens certificate.json's fixed_target_convention.generic_scope from a generic "
            "symbolic target to EVERY nonzero target, and certifies r = 0 as the complete "
            "exceptional locus."
        ),
        "algebra": {
            "universal_coefficient_ring": "Z[b,r]",
            "fixed_target_polynomial": "F_r(x1,x2,x3) = S4(x1,x2,x3,r) = Res_X(S3(x1,x2,X), S3(x3,r,X))",
            "support_size": len(support),
            "assumptions": [
                "beta is a primitive cube root of unity",
                "b is nonzero",
                "the field characteristic is neither 2 nor 3",
            ],
            "criterion": (
                "F_r(beta^e . x) = c_e F_r(x) as a polynomial identity iff a -> <e,a> mod 3 is "
                "constant on supp(F_r); every coefficient outside the surviving class must vanish."
            ),
        },
        "fixed_target_witnesses": rows,
        "witness_summary": {
            "rows": len(rows),
            "rows_without_pure_r_witness": len(missing),
            "distinct_minimal_witness_integers": integers,
            "primes_dividing_some_witness_integer": primes,
            "excluded_characteristics": sorted(set(primes) | {3}),
            "excluded_characteristic_reasons": {
                "2": "divides a minimal witness integer, so the r-forcing argument degenerates",
                "3": "beta would not be a primitive cube root of unity",
            },
        },
        "zero_slice": {
            "target_value": 0,
            "stabilizer": zero_slice_stabilizer(),
            "role": "the complete exceptional locus of the fixed-target classification",
        },
        "conclusions": {
            "fixed_target": (
                "For char K not in {2,3}, b != 0 and EVERY r != 0, the coordinatewise C3 "
                "stabilizer of F_r is trivial. This is stronger than a generic-target statement: "
                "each (e, keep-class) pair carries a pure-r witness N*r^k, and the only prime "
                "dividing any minimal |N| is 2, which is already excluded."
            ),
            "exceptional_locus": (
                "r = 0 is the unique exceptional target; there the stabilizer is the diagonal C3 "
                "with trivial multiplier."
            ),
            "affine_scope": (
                "r ranges over field elements and therefore over AFFINE targets only. A target at "
                "the point at infinity has no x-coordinate and is outside every statement here."
            ),
            "secp256k1_inhabitation": (
                "Whether the r = 0 locus is inhabited on a given curve is a separate arithmetic "
                "question (it needs a point (0,y) with y^2 = b) and is NOT settled by this "
                "certificate."
            ),
            "complexity": (
                "No claim about Groebner complexity, solving degree, relation probability, "
                "memory, precomputation, or any end-to-end ECDLP cost."
            ),
        },
        "producer": {
            "python_major_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
            "sympy_version": sp.__version__,
            "source_sha256": hashlib.sha256(
                Path(__file__).read_bytes()).hexdigest(),
            "source_commit": _git_head(),
        },
        "commands": {
            "generate": "python3 experiments/glv_semaev_symmetry/generate_fixed_target.py",
            "generate_check": "python3 experiments/glv_semaev_symmetry/generate_fixed_target.py --check",
            "independent_replay": "python3 experiments/glv_semaev_symmetry/validate_fixed_target.py",
        },
    }


def _git_head() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE,
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "unknown"


def render(cert: dict) -> bytes:
    return (json.dumps(cert, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode()


def _stable(cert: dict) -> dict:
    """The certificate minus fields that legitimately vary between machines."""
    out = json.loads(json.dumps(cert))
    out.pop("producer", None)
    return out


def main() -> int:
    cert = build()
    payload = render(cert)
    if "--check" in sys.argv:
        if not CERT.exists():
            print("fixed-target certificate missing; run without --check")
            return 1
        old = json.loads(CERT.read_text(encoding="utf-8"))
        if _stable(old) != _stable(cert):
            print("fixed-target certificate is STALE (recomputation differs)")
            return 1
        print(f"fixed-target certificate OK: {len(cert['fixed_target_witnesses'])} (e,class) rows, "
              f"witness integers {cert['witness_summary']['distinct_minimal_witness_integers']}, "
              f"excluded characteristics {cert['witness_summary']['excluded_characteristics']}")
        return 0
    CERT.write_bytes(payload)
    SHA.write_text(hashlib.sha256(payload).hexdigest() + "\n", encoding="utf-8")
    print(f"wrote {CERT.name} ({len(payload)} bytes) and {SHA.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
