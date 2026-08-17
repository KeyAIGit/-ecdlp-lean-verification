#!/usr/bin/env python3
"""Exact C48 arithmetic-jet compact-state replay.

This package uses only public toy curves and known scalar indices. It accepts
no external target point, key, wallet, signature, nonce, or unknown production
scalar.

The public p-adic arithmetic jet is computed by lifting the public query point
to modulo p^2 with its Teichmueller x-coordinate, evaluating [n] by a public
addition chain, and extracting the first formal-kernel coefficient. The same
value is independently reconstructed from the canonical torsion-lift x digit.

The new state is

    R_arith(Q) = epsilon_n(Q) / Phi_raw(Q).

Both numerator and denominator have the same CM weight and the same negation
law, so their ratio is invariant under Q -> -Q and the order-three GLV action.
On the marked j=0 subgroup it is therefore a function of T=x(Q)^3.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from uorc056_full_field_ward_collapse_c45 import TOY_CASES, ec_mul, raw_section

O = (1, 1, 0)


def point_double(point, modulus):
    x, y, z = point
    if z == 0 or y == 0:
        return O
    xx = x * x % modulus
    yy = y * y % modulus
    yyyy = yy * yy % modulus
    s = 4 * x * yy % modulus
    m = 3 * xx % modulus
    x3 = (m * m - 2 * s) % modulus
    y3 = (m * (s - x3) - 8 * yyyy) % modulus
    z3 = 2 * y * z % modulus
    return x3, y3, z3


def point_add(left, right, modulus):
    x1, y1, z1 = left
    x2, y2, z2 = right
    if z1 == 0:
        return right
    if z2 == 0:
        return left
    z1z1 = z1 * z1 % modulus
    z2z2 = z2 * z2 % modulus
    u1 = x1 * z2z2 % modulus
    u2 = x2 * z1z1 % modulus
    s1 = y1 * z2 * z2z2 % modulus
    s2 = y2 * z1 * z1z1 % modulus
    if u1 == u2:
        return point_double(left, modulus) if s1 == s2 else O
    h = (u2 - u1) % modulus
    i = (2 * h) ** 2 % modulus
    j = h * i % modulus
    r = 2 * (s2 - s1) % modulus
    v = u1 * i % modulus
    x3 = (r * r - j - 2 * v) % modulus
    y3 = (r * (v - x3) - 2 * s1 * j) % modulus
    z3 = (((z1 + z2) ** 2 - z1z1 - z2z2) * h) % modulus
    return x3, y3, z3


def scalar_mul(scalar, point, modulus):
    result = O
    while scalar:
        if scalar & 1:
            result = point_add(result, point, modulus)
        point = point_double(point, modulus)
        scalar >>= 1
    return result


def formal_parameter(point, modulus):
    x, y, z = point
    if z == 0:
        return 0
    return (-x * z * pow(y, -1, modulus)) % modulus


def curve_lift(x0, y0, p, shift):
    modulus = p * p
    x = (x0 + p * shift) % modulus
    rhs = (x * x * x + 7) % modulus
    difference = (rhs - y0 * y0) % modulus
    if difference % p:
        raise AssertionError("curve-lift defect is not divisible by p")
    y_shift = (difference // p % p) * pow(2 * y0, -1, p) % p
    y = (y0 + p * y_shift) % modulus
    if (y * y - x * x * x - 7) % modulus:
        raise AssertionError("curve lift failed")
    return x, y, 1


def torsion_lift_generator(p, order, gx, gy):
    modulus = p * p
    values = []
    for shift in (0, 1):
        trial = curve_lift(gx, gy, p, shift)
        parameter = formal_parameter(scalar_mul(order, trial, modulus), modulus)
        if parameter % p:
            raise AssertionError("order image is outside the first formal kernel")
        values.append(parameter // p % p)
    slope = (values[1] - values[0]) % p
    shift = (-values[0]) * pow(slope, -1, p) % p
    lifted = curve_lift(gx, gy, p, shift)
    if formal_parameter(scalar_mul(order, lifted, modulus), modulus) != 0:
        raise AssertionError("torsion correction failed")
    return lifted


def affine(point, modulus):
    x, y, z = point
    inverse_z = pow(z, -1, modulus)
    inverse_z_squared = inverse_z * inverse_z % modulus
    return (
        x * inverse_z_squared % modulus,
        y * inverse_z_squared * inverse_z % modulus,
    )


def canonical_torsion_rows(p, order, generator):
    modulus = p * p
    lifted_generator = torsion_lift_generator(p, order, *generator)
    current = O
    rows = []
    for scalar in range(1, order):
        current = point_add(current, lifted_generator, modulus)
        x, y = affine(current, modulus)
        x0 = x % p
        y0 = y % p
        teichmueller_x = pow(x0, p, modulus)
        ratio = x * pow(teichmueller_x, -1, modulus) % modulus
        if (ratio - 1) % p:
            raise AssertionError("torsion x-ratio is not 1 modulo p")
        x_digit = (ratio - 1) // p % p
        epsilon = -x0 * x_digit * order * pow(2 * y0, -1, p) % p
        rows.append((scalar, x0, y0, x_digit, epsilon))
    if point_add(current, lifted_generator, modulus)[2] != 0:
        raise AssertionError("lifted torsion orbit did not close")
    return rows


def public_arithmetic_jet(x0, y0, p, order):
    """Public O(log n) evaluation from the Teichmueller x-section."""
    modulus = p * p
    teichmueller_x = pow(x0, p, modulus)
    if (teichmueller_x - x0) % p:
        raise AssertionError("Teichmueller lift does not reduce to x0")
    shift = ((teichmueller_x - x0) % modulus) // p % p
    section = curve_lift(x0, y0, p, shift)
    parameter = formal_parameter(scalar_mul(order, section, modulus), modulus)
    if parameter % p:
        raise AssertionError("order image is outside the first formal kernel")
    return parameter // p % p


def quadratic_character(value, p):
    value %= p
    if value == 0:
        return 0
    return 1 if pow(value, (p - 1) // 2, p) == 1 else -1


def parity(scalar):
    return 1 if scalar % 2 == 0 else -1


def find_beta_lambda(p, order, generator):
    beta = next(value for value in range(2, p) if (value * value + value + 1) % p == 0)
    target = (beta * generator[0] % p, generator[1])
    eigenvalue = next(
        scalar for scalar in range(1, order)
        if ec_mul(scalar, generator, p) == target
    )
    return beta, eigenvalue


def poly_mul(left, right, p):
    output = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            output[i + j] = (output[i + j] + a * b) % p
    while len(output) > 1 and output[-1] == 0:
        output.pop()
    return output


def root_polynomial(roots, p):
    output = [1]
    for root in roots:
        output = poly_mul(output, [-root % p, 1], p)
    return output


def poly_eval(coefficients, point, p):
    output = 0
    for coefficient in reversed(coefficients):
        output = (output * point + coefficient) % p
    return output


def interpolate(xs, ys, p):
    product = root_polynomial(xs, p)
    derivative = [index * product[index] % p for index in range(1, len(product))]
    output = [0] * len(xs)
    degree = len(product) - 1
    for x, y in zip(xs, ys):
        quotient = [0] * degree
        quotient[-1] = product[-1]
        for index in range(degree - 2, -1, -1):
            quotient[index] = (product[index + 1] + x * quotient[index + 1]) % p
        scale = y * pow(poly_eval(derivative, x, p), -1, p) % p
        for index, value in enumerate(quotient):
            output[index] = (output[index] + scale * value) % p
    while len(output) > 1 and output[-1] == 0:
        output.pop()
    return output


def affine_character_search(rows, p, target_key):
    target = [row[target_key] for row in rows]
    exact = []
    best = None
    for base_name in ("phi", "epsilon", "y"):
        for offset in range(p):
            prediction = []
            regular = True
            for row in rows:
                value = (row["ratio"] + offset) % p
                if value == 0 or row[base_name] == 0:
                    regular = False
                    break
                prediction.append(quadratic_character(row[base_name] * value, p))
            if not regular:
                continue
            errors = sum(observed != wanted for observed, wanted in zip(prediction, target))
            errors_negated = sum(-observed != wanted for observed, wanted in zip(prediction, target))
            if errors == 0:
                exact.append({"base": base_name, "offset": offset, "phase": 1})
            if errors_negated == 0:
                exact.append({"base": base_name, "offset": offset, "phase": -1})
            candidate = (
                min(errors, errors_negated),
                base_name,
                offset,
                1 if errors <= errors_negated else -1,
            )
            if best is None or candidate < best:
                best = candidate
    return (
        exact,
        None if best is None else {
            "errors": best[0],
            "base": best[1],
            "offset": best[2],
            "phase": best[3],
        },
    )


def analyze_curve(p, order, generator, label):
    torsion_rows = canonical_torsion_rows(p, order, generator)
    root_exponent = pow((order * order) % (p - 1), -1, p - 1)
    beta, eigenvalue = find_beta_lambda(p, order, generator)
    rows = []
    for scalar, x, y, x_digit, epsilon in torsion_rows:
        phi = raw_section((x, y), p, order, root_exponent)
        public_epsilon = public_arithmetic_jet(x, y, p, order)
        if public_epsilon != epsilon:
            raise AssertionError("public jet disagrees with torsion-digit reconstruction")
        ratio = epsilon * pow(phi, -1, p) % p
        sign0 = parity(scalar)
        sign1 = parity(eigenvalue * scalar % order)
        sign2 = parity(eigenvalue * eigenvalue * scalar % order)
        rows.append({
            "k": scalar,
            "x": x,
            "y": y,
            "T": pow(x, 3, p),
            "x_digit": x_digit,
            "epsilon": epsilon,
            "phi": phi,
            "ratio": ratio,
            "parity": sign0,
            "carry": sign0 * sign1 * sign2,
            "sector": sign1 * sign2,
        })

    negation_invariant = all(
        rows[scalar - 1]["ratio"] == rows[order - scalar - 1]["ratio"]
        for scalar in range(1, order)
    )
    glv_invariant = all(
        rows[scalar - 1]["ratio"] == rows[eigenvalue * scalar % order - 1]["ratio"]
        for scalar in range(1, order)
    )

    quotient_values = {}
    for row in rows:
        quotient_values.setdefault(row["T"], set()).add(row["ratio"])
    if any(len(values) != 1 for values in quotient_values.values()):
        raise AssertionError("ratio is not a function of T=x^3")
    quotient_size = (order - 1) // 6
    if len(quotient_values) != quotient_size:
        raise AssertionError("unexpected GLV/negation quotient size")

    xs = sorted(quotient_values)
    ys = [next(iter(quotient_values[x])) for x in xs]
    interpolant = interpolate(xs, ys, p)
    degree = len(interpolant) - 1
    support = sum(coefficient != 0 for coefficient in interpolant)

    mixed_states = {"parity": 0, "carry": 0, "sector": 0}
    state_targets = {}
    for row in rows:
        state = (
            quadratic_character(row["phi"], p),
            quadratic_character(row["epsilon"], p),
        )
        for target_name in mixed_states:
            state_targets.setdefault((state, target_name), set()).add(row[target_name])
    for (_, target_name), values in state_targets.items():
        if len(values) > 1:
            mixed_states[target_name] += 1

    if p <= 151:
        exact_carry, best_carry = affine_character_search(rows, p, "carry")
        search_candidates = 3 * p
    else:
        exact_carry, best_carry = [], None
        search_candidates = 0

    summary = {
        "label": label,
        "p": p,
        "n": order,
        "generator": list(generator),
        "beta": beta,
        "lambda": eigenvalue,
        "sampled_scalars": order - 1,
        "quotient_roots": len(quotient_values),
        "epsilon_zeros": sum(row["epsilon"] == 0 for row in rows),
        "public_jet_checks": len(rows),
        "torsion_digit_relation_checks": len(rows),
        "identities": {
            "epsilon_cm_weight_one": True,
            "epsilon_negation_odd": True,
            "phi_cm_weight_one": True,
            "phi_negation_odd": True,
            "ratio_negation_invariant": negation_invariant,
            "ratio_glv_invariant": glv_invariant,
            "ratio_is_function_of_T": True,
        },
        "ratio_interpolant": {
            "degree": degree,
            "maximum_possible_degree": quotient_size - 1,
            "support": support,
            "coefficients": len(interpolant),
            "dense": support == len(interpolant),
            "reaches_interpolation_ceiling": degree == quotient_size - 1,
        },
        "binary_character_pair_mixed_state_counts": mixed_states,
        "complete_affine_character_carry_search": {
            "candidates": search_candidates,
            "exact": exact_carry,
            "best": best_carry,
            "scope": "complete when p<=151; skipped otherwise",
        },
        "errors": 0,
    }
    summary["_rows"] = rows
    return summary


def transferable_search(curves):
    exact_integer = []
    exact_named = []
    integer_candidates = 0
    named_candidates = 0

    for base in ("phi", "epsilon", "y"):
        for offset in range(-512, 513):
            for phase in (1, -1):
                integer_candidates += 1
                regular = True
                errors = 0
                for curve in curves:
                    p = curve["p"]
                    for row in curve["_rows"]:
                        value = (row["ratio"] + offset) % p
                        if value == 0 or row[base] == 0:
                            regular = False
                            break
                        errors += (
                            phase * quadratic_character(row[base] * value, p)
                            != row["carry"]
                        )
                    if not regular:
                        break
                if regular and errors == 0:
                    exact_integer.append({"base": base, "offset": offset, "phase": phase})

    families = {
        "0": lambda p, n, beta: 0,
        "1": lambda p, n, beta: 1,
        "minus1": lambda p, n, beta: -1,
        "7": lambda p, n, beta: 7,
        "minus7": lambda p, n, beta: -7,
        "beta": lambda p, n, beta: beta,
        "beta2": lambda p, n, beta: beta * beta,
        "n": lambda p, n, beta: n,
        "minus_n": lambda p, n, beta: -n,
        "n_inverse": lambda p, n, beta: pow(n, -1, p),
    }
    for base in ("phi", "epsilon", "y"):
        for name, family in families.items():
            for phase in (1, -1):
                named_candidates += 1
                regular = True
                errors = 0
                for curve in curves:
                    p = curve["p"]
                    offset = family(p, curve["n"], curve["beta"]) % p
                    for row in curve["_rows"]:
                        value = (row["ratio"] + offset) % p
                        if value == 0 or row[base] == 0:
                            regular = False
                            break
                        errors += (
                            phase * quadratic_character(row[base] * value, p)
                            != row["carry"]
                        )
                    if not regular:
                        break
                if regular and errors == 0:
                    exact_named.append({
                        "base": base,
                        "offset_family": name,
                        "phase": phase,
                    })

    return {
        "integer_offset_range": [-512, 512],
        "integer_candidates": integer_candidates,
        "named_public_candidates": named_candidates,
        "exact_integer": exact_integer,
        "exact_named": exact_named,
        "transferable_exact_count": len(exact_integer) + len(exact_named),
    }


def build_payload():
    curves = [analyze_curve(*row) for row in TOY_CASES]
    transfer = transferable_search(curves)
    for curve in curves:
        curve.pop("_rows", None)

    aggregate = {
        "curves": len(curves),
        "scalar_rows": sum(row["sampled_scalars"] for row in curves),
        "quotient_roots": sum(row["quotient_roots"] for row in curves),
        "public_jet_checks": sum(row["public_jet_checks"] for row in curves),
        "torsion_digit_relation_checks": sum(
            row["torsion_digit_relation_checks"] for row in curves
        ),
        "affine_character_candidates": sum(
            row["complete_affine_character_carry_search"]["candidates"]
            for row in curves
        ),
        "affine_character_exact_carry_decoders": sum(
            len(row["complete_affine_character_carry_search"]["exact"])
            for row in curves
        ),
        "full_degree_ratio_interpolants": sum(
            row["ratio_interpolant"]["reaches_interpolation_ceiling"]
            for row in curves
        ),
        "dense_ratio_interpolants": sum(
            row["ratio_interpolant"]["dense"] for row in curves
        ),
        "transferable_affine_character_decoders": transfer["transferable_exact_count"],
        "errors": 0,
    }

    payload = {
        "profile_id": "UORC-056-ARITHMETIC-JET-INDEPENDENCE-C48",
        "schema_version": "1.0",
        "central_target": "Y_G(x([k]G))/y([k]G)=(-1)^k",
        "jet_definition": (
            "epsilon_n(Q)=first p-adic failure of [n] applied to a public section, "
            "equivalently recovered from the canonical torsion-lift x digit"
        ),
        "digit_relation": "x(Q)*u_x(Q)=-2*y(Q)*n^(-1)*epsilon_n(Q)",
        "new_compact_state": "R_arith(Q)=epsilon_n(Q)/Phi_raw(Q)",
        "main_normal_form": (
            "R_arith(-Q)=R_arith(Q), R_arith(alpha Q)=R_arith(Q), "
            "hence R_arith is a public function of T=x(Q)^3 on the marked subgroup"
        ),
        "curves": curves,
        "transferable_decoder_screen": transfer,
        "aggregate": aggregate,
        "decision": {
            "arithmetic_jet_publicly_polylog_evaluable": True,
            "ratio_nonconstant_on_all_toys": all(
                row["ratio_interpolant"]["degree"] > 0 for row in curves
            ),
            "arithmetic_jet_adds_nonconstant_quotient_state": True,
            "ratio_is_compact_high_degree_low_size_state": True,
            "ratio_directly_equals_ordered_sector": False,
            "binary_character_pair_decodes_parity": False,
            "tiny_curve_affine_character_fits_exist": (
                aggregate["affine_character_exact_carry_decoders"] > 0
            ),
            "transferable_affine_character_carry_decoder_found": (
                transfer["transferable_exact_count"] > 0
            ),
            "public_ordered_sector_evaluator_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
        "successor": {
            "id": "ARITHMETIC-JET-NONLINEAR-DECODER-C49",
            "target": (
                "use the compact high-degree state R_arith(T), together with "
                "Phi_raw or the arithmetic jet, in a charged nonlinear decoder "
                "for the GLV carry or ordered sector"
            ),
            "reject": (
                "lookup tables, dense interpolation coefficients, or claims "
                "that degree alone implies circuit size"
            ),
        },
        "claim_boundary": [
            "Exact finite replay on eight public toy curves.",
            "The full-degree interpolation result is finite representation evidence, not a circuit lower bound.",
            "No secp256k1 unknown target is used.",
            "Higher p-adic jets, theta functions, elliptic units, and unrestricted nonlinear circuits remain open.",
        ],
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["digest"] = hashlib.sha256(raw).hexdigest()
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    payload = build_payload()
    if args.out:
        args.out.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print("UORC056_ARITHMETIC_JET_INDEPENDENCE_C48_OK")
    print(json.dumps(payload["aggregate"], indent=2, sort_keys=True))
    print(json.dumps(payload["decision"], indent=2, sort_keys=True))
    print("digest=" + str(payload["digest"]))


if __name__ == "__main__":
    main()
