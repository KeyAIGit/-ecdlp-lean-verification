#!/usr/bin/env python3
"""Exact carry/sector factorization of the UORC-056 C3 oriented root.

V14 decomposes the canonical parity signs on a public GLV orbit into an
invariant majority component and a four-branch sector selector.  This replay
shows that the two pieces can be normalized more sharply.

For
    s0 = sigma(Q),
    s1 = sigma(alpha(Q)),
    s2 = sigma(alpha^2(Q)),
define
    carry = s0*s1*s2,
    kappa0 = s1*s2,
    kappa1 = s2*s0,
    kappa2 = s0*s1.

Then sigma(Q)=carry*kappa0.  The three kappa bits form a Klein-four state,
and the V14 field selector u=x*B/A is their C3 Fourier transform.  Conversely
one sector bit evaluated on the three public GLV rotations recovers u.

The replay uses only frozen toy curves and fixed known scalars.  It accepts no
external point or production-sized unknown scalar.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from uorc056_cm_threefold_root_decomposition import decompose_mod_three
from uorc056_toy_factory import DEFAULT_INSTANCES, build_fixture, poly_eval

PROFILE_ID = "UORC-056-CARRY-SECTOR-FACTORIZATION-V15"
DEFAULT_OUTPUT = Path("experiments/uorc056/carry_sector_factorization_results.json")


def stable_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def point_sign(k: int) -> int:
    return -1 if k & 1 else 1


def sign_to_field(sign: int, p: int) -> int:
    if sign not in (-1, 1):
        raise ValueError("sign must be +/-1")
    return 1 if sign == 1 else p - 1


def sector_phase(u: int, p: int) -> int:
    """h(u)=(u^3+u^2-2u+6)/6 in F_p."""
    inv6 = pow(6, -1, p)
    return (u**3 + u**2 - 2 * u + 6) * inv6 % p


def classify_branch(signs: Sequence[int]) -> str:
    s0, s1, s2 = signs
    if s0 == s1 == s2:
        return "uniform"
    if s1 == s2:
        return "minority_0"
    if s0 == s2:
        return "minority_1"
    if s0 == s1:
        return "minority_2"
    raise AssertionError("three +/-1 signs must be uniform or have one minority")


def expected_selector(branch: str, beta: int, p: int) -> int:
    if branch == "uniform":
        return 0
    if branch == "minority_0":
        return (-2) % p
    if branch == "minority_1":
        return (-2 * beta * beta) % p
    if branch == "minority_2":
        return (-2 * beta) % p
    raise ValueError(f"unknown branch {branch}")


def truth_table(beta: int, p: int) -> list[dict[str, Any]]:
    """Return the four possible C3 orbit states and verify the exact formulas."""
    if beta == 1 or pow(beta, 3, p) != 1:
        raise AssertionError("beta must be a nontrivial cube root of unity")
    rows: list[dict[str, Any]] = []
    representatives = {
        "uniform": (1, 1, 1),
        "minority_0": (-1, 1, 1),
        "minority_1": (1, -1, 1),
        "minority_2": (1, 1, -1),
    }
    beta2 = beta * beta % p
    for branch, signs in representatives.items():
        s0, s1, s2 = signs
        carry = s0 * s1 * s2
        kappas = (s1 * s2, s2 * s0, s0 * s1)
        if kappas[0] * kappas[1] * kappas[2] != 1:
            raise AssertionError("kappa state did not lie in the Klein four set")
        u = -(
            sign_to_field(kappas[0], p)
            + beta2 * sign_to_field(kappas[1], p)
            + beta * sign_to_field(kappas[2], p)
        ) % p
        expected_u = expected_selector(branch, beta, p)
        if u != expected_u:
            raise AssertionError("C3 Fourier selector truth table failed")
        phases = (
            sector_phase(u, p),
            sector_phase(beta * u % p, p),
            sector_phase(beta2 * u % p, p),
        )
        expected_phases = tuple(sign_to_field(kappa, p) for kappa in kappas)
        if phases != expected_phases:
            raise AssertionError("sector polynomial did not recover the kappa orbit")
        if sign_to_field(carry * kappas[0], p) != sign_to_field(s0, p):
            raise AssertionError("carry times sector did not recover parity")
        rows.append(
            {
                "branch": branch,
                "signs": list(signs),
                "carry": carry,
                "kappas": list(kappas),
                "selector_u": u,
            }
        )
    return rows


def curve_record(instance) -> dict[str, Any]:
    p = instance.curve.p
    n = instance.subgroup_order
    beta = int(instance.cm_beta)
    lam = int(instance.glv_lambda)
    beta2 = beta * beta % p
    inv2 = pow(2, -1, p)
    inv6 = pow(6, -1, p)

    table = truth_table(beta, p)
    fixture = build_fixture(instance, include_all_markers=True)

    branch_counts = {
        "uniform": 0,
        "minority_0": 0,
        "minority_1": 0,
        "minority_2": 0,
    }
    carry_counts = {"+1": 0, "-1": 0}
    sector_counts = {"+1": 0, "-1": 0}
    state_counts = {
        "(+,+,+)": 0,
        "(+,-,-)": 0,
        "(-,+,-)": 0,
        "(-,-,+)": 0,
    }
    scalar_checks = 0

    for marker in range(1, n):
        root = fixture["marked_roots"][str(marker)]["coefficients_low_to_high"]
        A, B, _C = decompose_mod_three(root, p)
        marked_generator = instance.curve.mul(marker, instance.generator)
        if marked_generator is None:
            raise AssertionError("marked generator became infinity")

        for k in range(1, n):
            Q = instance.curve.mul(k, marked_generator)
            if Q is None:
                raise AssertionError("nonzero marked multiple became infinity")
            x, y = Q
            t = pow(x, 3, p)

            k1 = lam * k % n
            k2 = lam * k1 % n
            s0 = point_sign(k)
            s1 = point_sign(k1)
            s2 = point_sign(k2)
            signs = (s0, s1, s2)
            branch = classify_branch(signs)
            branch_counts[branch] += 1

            carry = s0 * s1 * s2
            kappas = (s1 * s2, s2 * s0, s0 * s1)
            if kappas[0] * kappas[1] * kappas[2] != 1:
                raise AssertionError("Klein-four product failed")
            carry_counts["+1" if carry == 1 else "-1"] += 1
            sector_counts["+1" if kappas[0] == 1 else "-1"] += 1
            state_key = "".join("+" if value == 1 else "-" for value in kappas)
            state_key = f"({state_key[0]},{state_key[1]},{state_key[2]})"
            if state_key not in state_counts:
                raise AssertionError("unexpected kappa orbit state")
            state_counts[state_key] += 1

            Aval = poly_eval(A, t, p)
            Bval = poly_eval(B, t, p)
            if Aval == 0:
                raise AssertionError("V14 invariant A vanished on a subgroup orbit")
            u = x * Bval * pow(Aval, -1, p) % p
            expected_u = expected_selector(branch, beta, p)
            if u != expected_u:
                raise AssertionError("V14 selector did not match the sign branch")

            kappa_fields = tuple(sign_to_field(value, p) for value in kappas)
            selector_from_bits = -(
                kappa_fields[0] + beta2 * kappa_fields[1] + beta * kappa_fields[2]
            ) % p
            if selector_from_bits != u:
                raise AssertionError("three sector bits did not reconstruct u")

            phase0 = sector_phase(u, p)
            phase1 = sector_phase(beta * u % p, p)
            phase2 = sector_phase(beta2 * u % p, p)
            if (phase0, phase1, phase2) != kappa_fields:
                raise AssertionError("sector phase polynomial failed")

            carry_field = sign_to_field(carry, p)
            if carry_field * phase0 % p != sign_to_field(s0, p):
                raise AssertionError("carry-sector parity factorization failed")

            # A/y is not a third independent target:
            # A/y = carry * (1 + u^3/6).
            A_over_y = Aval * pow(y, -1, p) % p
            expected_A_over_y = carry_field * (1 + pow(u, 3, p) * inv6) % p
            if A_over_y != expected_A_over_y:
                raise AssertionError("A/y did not collapse to carry and sector")

            # Reconcile with the direct V14 reconstruction.
            direct_factor = (1 + u - u * u * inv2) % p
            if A_over_y * direct_factor % p != sign_to_field(s0, p):
                raise AssertionError("V14 direct reconstruction drifted")

            # The sector bit is an x-only Kummer involution:
            # J(x)=Y(beta*x)Y(beta^2*x)/(x^3+7)=s1*s2.
            y0 = poly_eval(root, x, p)
            y1 = poly_eval(root, beta * x % p, p)
            y2 = poly_eval(root, beta2 * x % p, p)
            F = (t + 7) % p
            if F == 0 or F != y * y % p:
                raise AssertionError("curve value became zero or inconsistent")
            invF = pow(F, -1, p)
            J0 = y1 * y2 * invF % p
            J1 = y2 * y0 * invF % p
            J2 = y0 * y1 * invF % p
            if (J0, J1, J2) != kappa_fields:
                raise AssertionError("Kummer involution did not match sector bits")
            if J0 * J0 % p != 1 or J0 * J1 * J2 % p != 1:
                raise AssertionError("Kummer involution identities failed")

            scalar_checks += 1

    if scalar_checks != (n - 1) ** 2:
        raise AssertionError("curve scalar-check total drifted")

    return {
        "id": instance.instance_id,
        "p": p,
        "n": n,
        "marked_roots": n - 1,
        "scalar_evaluations": scalar_checks,
        "branch_counts": branch_counts,
        "carry_counts": carry_counts,
        "sector_bit_counts": sector_counts,
        "kappa_state_counts": state_counts,
        "truth_table": table,
    }


def run() -> dict[str, Any]:
    rows = [curve_record(instance) for instance in DEFAULT_INSTANCES]
    total_roots = sum(row["marked_roots"] for row in rows)
    total_checks = sum(row["scalar_evaluations"] for row in rows)
    aggregate_branches = {
        key: sum(row["branch_counts"][key] for row in rows)
        for key in ("uniform", "minority_0", "minority_1", "minority_2")
    }
    aggregate_carry = {
        key: sum(row["carry_counts"][key] for row in rows) for key in ("+1", "-1")
    }
    aggregate_sector = {
        key: sum(row["sector_bit_counts"][key] for row in rows)
        for key in ("+1", "-1")
    }
    aggregate_states = {
        key: sum(row["kappa_state_counts"][key] for row in rows)
        for key in ("(+,+,+)", "(+,-,-)", "(-,+,-)", "(-,-,+)")
    }

    if total_roots != 438 or total_checks != 46260:
        raise AssertionError("frozen replay totals drifted")
    if aggregate_branches != {
        "uniform": 12096,
        "minority_0": 11388,
        "minority_1": 11388,
        "minority_2": 11388,
    }:
        raise AssertionError("V14 branch partition drifted")
    if aggregate_carry != {"+1": 23130, "-1": 23130}:
        raise AssertionError("carry balance drifted")
    if aggregate_sector != {"+1": 23484, "-1": 22776}:
        raise AssertionError("sector balance drifted")
    if aggregate_states != {
        "(+,+,+)": 12096,
        "(+,-,-)": 11388,
        "(-,+,-)": 11388,
        "(-,-,+)": 11388,
    }:
        raise AssertionError("Klein-four state partition drifted")

    return {
        "schema_version": "1.0",
        "profile_id": PROFILE_ID,
        "exact_factorization": {
            "orbit_signs": "s_i=sigma(alpha^i(Q)), i=0,1,2",
            "carry": "c=s0*s1*s2=(-1)^gamma",
            "sector_bits": [
                "kappa0=s1*s2",
                "kappa1=s2*s0",
                "kappa2=s0*s1",
            ],
            "parity": "sigma(Q)=c*kappa0",
            "klein_state": "kappa0*kappa1*kappa2=1",
            "sector_selector_dft": (
                "u=-(kappa0+beta^2*kappa1+beta*kappa2)"
            ),
            "sector_phase_polynomial": (
                "h(u)=(u^3+u^2-2u+6)/6; "
                "kappa_i=h(beta^i*u)"
            ),
            "A_mode_collapse": "A/y=c*(1+u^3/6)",
            "kummer_involution": (
                "J_G(x)=Y_G(beta*x)Y_G(beta^2*x)/(x^3+7)=kappa0; "
                "J_G^2=1 and prod_i J_G(beta^i*x)=1 on K_H"
            ),
        },
        "symmetry_split": {
            "carry": "C3/GLV-invariant and anti-invariant under Q -> -Q",
            "sector_bit": "Kummer-invariant under Q -> -Q and non-invariant along the C3/GLV orbit",
            "constant_call_equivalence": (
                "one sector-bit evaluator on Q,alpha(Q),alpha^2(Q) reconstructs "
                "the full four-state selector u by the displayed DFT"
            ),
            "division_polynomial_consequence": (
                "V13 finite multiplicative division-polynomial characters are "
                "C3-invariant, so they cannot equal the non-invariant sector bit"
            ),
        },
        "exact_replay": {
            "curves": len(rows),
            "marked_roots": total_roots,
            "scalar_evaluations": total_checks,
            "branch_counts": aggregate_branches,
            "carry_counts": aggregate_carry,
            "sector_bit_counts": aggregate_sector,
            "kappa_state_counts": aggregate_states,
            "curve_rows": rows,
        },
        "decision": (
            "V14_A_mode_is_not_an_independent_observable; canonical parity "
            "factors_exactly_into_one_GLV_carry_bit_and_one_Kummer_sector_bit"
        ),
        "next_frontier": [
            "seek or lower-bound a public decoder for the GLV carry c(Q)",
            "seek or lower-bound the Kummer involution J_G(x(Q))",
            "test additive mixtures of distinct CM weights; multiplicative division-polynomial monomials are already closed by V13",
            "search for shared evaluation of carry and sector rather than constructing dense A and B separately",
            "charge representation construction, branch selection, memory and all public GLV calls",
        ],
        "scientific_boundary": (
            "V15 is an exact two-bit normal form and constant-call equivalence, "
            "not a public decoder and not a sub-square-root algorithm."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    text = stable_json(run())
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("V15 carry-sector artifact drift")
        print("UORC056_CARRY_SECTOR_FACTORIZATION_OK")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
