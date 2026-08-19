#!/usr/bin/env python3
"""Per-curve exact deformation replay for C52."""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from uorc056_c52_deformation_core import (
    Curve, DualCurve, invariant_tangent_scalar, interpolation_polynomial,
    is_prime, lift_point, point_count, polynomial_stats, quadratic_character,
    torsion_lift_basis, vertical_tangent_point,
)
from uorc056_c52_analysis_primitives import (
    FEATURE_NAMES, PAIR_FEATURES, build_feature_row, coefficient_values,
    mixed_parity_collisions, tuple_mixed,
)


def analyze_curve(row, label: str) -> tuple[dict[str, Any], dict[str, Any]]:
    p, n, generator, beta, lam = row
    curve = Curve(p)
    if not is_prime(p) or not is_prime(n):
        raise AssertionError("fixture moduli are not prime")
    if point_count(curve) != n:
        raise AssertionError("curve order mismatch")
    if curve.mul(n, generator) is not None:
        raise AssertionError("generator order mismatch")
    if pow(beta, 3, p) != 1 or beta == 1:
        raise AssertionError("bad beta")
    if (lam * lam + lam + 1) % n:
        raise AssertionError("bad lambda")
    if curve.mul(lam, generator, n) != (beta * generator[0] % p, generator[1]):
        raise AssertionError("GLV action mismatch")

    tangent_a_g, tangent_b_g, _ = torsion_lift_basis(curve, n, generator)
    ua_g, va_g = tangent_a_g
    ub_g, vb_g = tangent_b_g
    omega_a_g = ua_g * pow(2 * generator[1], -1, p) % p
    omega_b_g = ub_g * pow(2 * generator[1], -1, p) % p
    det_g = (ua_g * vb_g - ub_g * va_g) % p
    if not all((ua_g, va_g, ub_g, vb_g, omega_a_g, omega_b_g, det_g)):
        raise AssertionError("singular anchor chart")
    anchor = {
        "uaG": ua_g,
        "vaG": va_g,
        "ubG": ub_g,
        "vbG": vb_g,
        "omegaAG": omega_a_g,
        "omegaBG": omega_b_g,
        "detG": det_g,
    }
    context = {
        "p": p, "n": n, "b": curve.b,
        "xG": generator[0], "yG": generator[1],
        "beta": beta, "lambda": lam, **anchor,
    }

    dual_a = DualCurve(curve, 1, 0)
    dual_b = DualCurve(curve, 0, 1)
    dual_scale = DualCurve(curve, 4 * curve.a, 6 * curve.b)
    lift_g_a = lift_point(curve, n, generator, 1, 0)
    lift_g_b = lift_point(curve, n, generator, 0, 1)
    lift_g_scale = lift_point(curve, n, generator, 4 * curve.a, 6 * curve.b)
    fixed_dual = DualCurve(curve)
    vertical_g = vertical_tangent_point(curve, generator, 1)

    points: dict[int, tuple[int, int]] = {}
    tangents: dict[int, tuple[tuple[int, int], tuple[int, int]]] = {}
    columns = {name: [] for name in FEATURE_NAMES}
    parities: list[int] = []
    horizontal_checks = scaling_checks = vertical_checks = 0

    for k in range(1, n):
        point = curve.mul(k, generator, n)
        if point is None:
            raise AssertionError("unexpected identity")
        tangent_a, tangent_b, jet = torsion_lift_basis(curve, n, point)
        if jet.value != 0 or jet.dx == 0:
            raise AssertionError("torsion jet contract failed")
        points[k] = point
        tangents[k] = (tangent_a, tangent_b)

        if dual_a.mul(k, lift_g_a, n) != lift_point(curve, n, point, 1, 0):
            raise AssertionError("a transport failed")
        if dual_b.mul(k, lift_g_b, n) != lift_point(curve, n, point, 0, 1):
            raise AssertionError("b transport failed")
        scale_lift = lift_point(curve, n, point, 4 * curve.a, 6 * curve.b)
        if dual_scale.mul(k, lift_g_scale, n) != scale_lift:
            raise AssertionError("scale transport failed")
        horizontal_checks += 3

        if scale_lift[0].epsilon != 2 * point[0] % p:
            raise AssertionError("scale x failed")
        if scale_lift[1].epsilon != 3 * point[1] % p:
            raise AssertionError("scale y failed")
        inv_6b = pow(6 * curve.b, -1, p)
        if tangent_b != (
            2 * inv_6b * point[0] % p,
            3 * inv_6b * point[1] % p,
        ):
            raise AssertionError("b direction is not scaling")
        scaling_checks += 2

        vertical_q = fixed_dual.mul(k, vertical_g, n)
        if vertical_q is None or invariant_tangent_scalar(vertical_q) != k % p:
            raise AssertionError("vertical tangent scalar recovery failed")
        vertical_checks += 1

        feature_row = build_feature_row(p, point, tangent_a, tangent_b, anchor)
        for name, value in feature_row.items():
            columns[name].append(value)
        parities.append(k & 1)

    negation_checks = cm_checks = 0
    for k in range(1, n):
        opposite = n - k
        point = points[k]
        if points[opposite] != curve.neg(point):
            raise AssertionError("negation point mismatch")
        (ua, va), (ub, vb) = tangents[k]
        (una, vna), (unb, vnb) = tangents[opposite]
        if (una, vna, unb, vnb) != (ua, -va % p, ub, -vb % p):
            raise AssertionError("negation covariance failed")
        negation_checks += 1

        image = lam * k % n
        if points[image] != (beta * point[0] % p, point[1]):
            raise AssertionError("CM point mismatch")
        (uap, vap), (ubp, vbp) = tangents[image]
        if (uap, vap, ubp, vbp) != (
            beta * beta * ua % p,
            beta * va % p,
            beta * ub % p,
            vb,
        ):
            raise AssertionError("CM tangent covariance failed")
        cm_checks += 1

    quotient: dict[int, tuple[int, int]] = {}
    for k in range(1, n):
        x, y = points[k]
        (ua, va), _ = tangents[k]
        t = x**3 % p
        r_value = x * ua % p
        s_value = x * x % p * va % p * pow(y, -1, p) % p
        if t in quotient and quotient[t] != (r_value, s_value):
            raise AssertionError("CM quotient not invariant")
        quotient[t] = (r_value, s_value)
        if (2 * (t + 7) * s_value - t * (3 * r_value + 1)) % p:
            raise AssertionError("CM quotient relation failed")
    if len(quotient) != (n - 1) // 6:
        raise AssertionError("quotient root count mismatch")
    ts = sorted(quotient)
    r_poly = interpolation_polynomial(ts, [quotient[t][0] for t in ts], p)
    s_poly = interpolation_polynomial(ts, [quotient[t][1] for t in ts], p)

    target_signs = [-1 if parity else 1 for parity in parities]
    character_table = [quadratic_character(value, p) for value in range(p)]
    feature_status: dict[str, Any] = {}
    for name, values in columns.items():
        survivors = []
        valid = 0
        for shift in range(p):
            signs = [character_table[(value + shift) % p] for value in values]
            if 0 in signs:
                continue
            valid += 1
            if signs == target_signs:
                survivors.append({"shift": shift, "phase": 1})
            elif signs == [-value for value in target_signs]:
                survivors.append({"shift": shift, "phase": -1})
        feature_status[name] = {
            "distinct_values": len(set(values)),
            "mixed_parity_collisions": mixed_parity_collisions(values, parities),
            "valid_affine_character_atoms": valid,
            "affine_character_survivors": survivors,
        }

    direction_survivors = []
    direction_raw = defaultdict(list)
    directions = [(1, slope) for slope in range(p)] + [(0, 1)]
    for da, db in directions:
        for output in ("u", "v", "omega", "position"):
            values = []
            for k in range(1, n):
                x, y = points[k]
                (ua, va), (ub, vb) = tangents[k]
                u = (da * ua + db * ub) % p
                v = (da * va + db * vb) % p
                if output == "u":
                    value = u
                elif output == "v":
                    value = v
                elif output == "omega":
                    value = u * pow(2 * y, -1, p) % p
                else:
                    value = (x * v - y * u) % p
                values.append(value)
            if mixed_parity_collisions(values, parities) == 0:
                direction_raw[output].append((da, db))
            signs = [character_table[value] for value in values]
            if 0 not in signs:
                if signs == target_signs:
                    direction_survivors.append((da, db, output, 1))
                elif signs == [-value for value in target_signs]:
                    direction_survivors.append((da, db, output, -1))

    pair_status = {}
    for left, right in PAIR_FEATURES:
        tuples = list(zip(columns[left], columns[right]))
        pair_status[f"{left}|{right}"] = {
            "distinct_values": len(set(tuples)),
            "mixed_parity_collision": tuple_mixed(tuples, parities),
        }

    result = {
        "label": label,
        "p": p,
        "n": n,
        "rows": n - 1,
        "horizontal_transport_checks": horizontal_checks,
        "weierstrass_scaling_checks": scaling_checks,
        "vertical_scalar_recovery_checks": vertical_checks,
        "negation_covariance_checks": negation_checks,
        "cm_covariance_checks": cm_checks,
        "feature_status": feature_status,
        "pair_state_status": pair_status,
        "projective_direction_character_survivors": direction_survivors,
        "projective_direction_raw_separators": dict(direction_raw),
        "cm_quotient": {
            "roots": len(ts),
            "R_x_times_ua": polynomial_stats(r_poly),
            "S_x2_va_over_y": polynomial_stats(s_poly),
            "relation": "2(T+7)S=T(3R+1)",
        },
        "identities": {
            "finite_etale_unique_torsion_lift_replayed": True,
            "horizontal_scalar_relation_preserved": True,
            "fixed_curve_vertical_tangent_recovers_full_scalar": True,
            "weierstrass_scaling_is_pure_gauge": True,
            "b_direction_is_pure_scaling": True,
            "negation_covariance": True,
            "cm_covariance": True,
            "a_deformation_cm_quotient_relation": True,
        },
        "errors": 0,
    }
    auxiliary = {
        "context": context,
        "coefficients": coefficient_values(context),
        "feature_columns": columns,
        "parities": parities,
    }
    return result, auxiliary
