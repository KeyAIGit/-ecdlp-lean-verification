#!/usr/bin/env python3
"""Exact connection-defect and nonlinear moduli-state analysis for C53."""
from __future__ import annotations

from itertools import combinations
from typing import Any

from uorc056_c53_connection_core import (
    StateRow, XorBasis, bit_vector, charged_columns, connection_cocycle_rhs,
    curve_rows, defect, gauge_difference, mixed_parity_collisions, normalized,
    quadratic_character, recover_multiplier_from_defect, structural_constants,
)

PAIR_STATES = (
    ("U", "V"),
    ("OA", "OB"),
    ("D", "OB"),
    ("P", "OB"),
)

SCALAR_STATES = ("V", "OA", "D", "P", "UV", "V3", "U2V")


def tuple_mixed(values: list[tuple[int, ...]], rows: list[StateRow]) -> bool:
    seen: dict[tuple[int, ...], int] = {}
    for value, row in zip(values, rows):
        parity = row.k & 1
        if value in seen and seen[value] != parity:
            return True
        seen[value] = parity
    return False


def connection_analysis(
    rows: list[StateRow], context: dict[str, int]
) -> dict[str, Any]:
    p, n, lam = context["p"], context["n"], context["lambda"]
    c = {row.k: row.omega_a for row in rows}
    f = {row.k: row.omega_b for row in rows}
    cG = c[1]
    if cG == 0:
        raise AssertionError("connection anchor unexpectedly zero")

    recovery_checks = 0
    anchor_zero_checks = 0
    gauge_checks = 0
    odd_checks = 0
    for row in rows:
        k = row.k
        delta = defect(c[k], k, cG, p)
        if recover_multiplier_from_defect(c[k], delta, cG, p) != k % p:
            raise AssertionError("defect oracle did not recover multiplier modulo p")
        recovery_checks += 1

        c0G = 0
        c0Q = (c[k] - cG) % p
        if defect(c0Q, k, c0G, p) != c0Q:
            raise AssertionError("anchor-zero defect is not direct point state")
        anchor_zero_checks += 1

        delta_prime = defect((c[k] + f[k]) % p, k, (cG + f[1]) % p, p)
        expected = (delta + gauge_difference(f[k], k, f[1], p)) % p
        if delta_prime != expected:
            raise AssertionError("connection gauge transformation failed")
        gauge_checks += 1

        neg = n - k
        if defect(c[neg], -1, c[k], p) != 0:
            raise AssertionError("odd connection has nonzero negation defect")
        odd_checks += 1

    cocycle_checks = 0
    multiplier_pairs = ((2, 3), (2, lam), (lam, lam))
    for row in rows:
        j = row.k
        for a, b in multiplier_pairs:
            bj = b * j % n
            abj = a * b * j % n
            if bj == 0 or abj == 0:
                raise AssertionError("unexpected identity in prime-order chart")
            delta_ab = defect(c[abj], a * b, c[j], p)
            delta_a_at_b = defect(c[abj], a, c[bj], p)
            delta_b = defect(c[bj], b, c[j], p)
            if delta_ab != connection_cocycle_rhs(delta_a_at_b, a, delta_b, p):
                raise AssertionError("multiplier connection cocycle failed")
            cocycle_checks += 1

    return {
        "rows": len(rows),
        "nonzero_anchor_recovery_checks": recovery_checks,
        "anchor_zero_direct_state_checks": anchor_zero_checks,
        "gauge_coboundary_checks": gauge_checks,
        "odd_negation_defect_checks": odd_checks,
        "multiplier_cocycle_checks": cocycle_checks,
        "full_integer_recovery_when_n_below_p": n < p,
        "classification": {
            "functorial_or_multiplicative": "delta=0",
            "anchor_zero": "delta_k(G)=c(Q), so the wrapper adds no information",
            "nonzero_anchor": "k=(c(Q)-delta_k(G))/c(G) in the base field",
            "gauge_change": "delta changes by f(Q)-k f(G)",
        },
    }


def covariance_analysis(
    rows: list[StateRow], context: dict[str, int], columns: dict[str, list[int]]
) -> dict[str, Any]:
    p, n, beta, lam = (
        context["p"], context["n"], context["beta"], context["lambda"]
    )
    idx = {row.k: i for i, row in enumerate(rows)}
    neg_checks = glv_checks = quotient_checks = 0
    for i, row in enumerate(rows):
        neg_i = idx[n - row.k]
        glv_i = idx[lam * row.k % n]
        glv2_i = idx[lam * lam * row.k % n]

        if columns["U"][neg_i] != columns["U"][i]:
            raise AssertionError("U negation covariance failed")
        if columns["V"][neg_i] != -columns["V"][i] % p:
            raise AssertionError("V negation covariance failed")
        if columns["U"][glv_i] != beta * beta % p * columns["U"][i] % p:
            raise AssertionError("U GLV weight failed")
        if columns["V"][glv_i] != beta * columns["V"][i] % p:
            raise AssertionError("V GLV weight failed")
        neg_checks += 1
        glv_checks += 2

        for name in ("T", "R", "S"):
            if not (
                columns[name][neg_i]
                == columns[name][glv_i]
                == columns[name][glv2_i]
                == columns[name][i]
            ):
                raise AssertionError("GLV/Kummer quotient state is not invariant")
        quotient_checks += 3

    factorization_checks = 0
    anchor_row = rows[0]
    xg, yg = anchor_row.point
    rg = anchor_row.cm_r
    if rg == 0:
        raise AssertionError("zero anchor R in charged-neutral chart")
    for i, row in enumerate(rows):
        x, y = row.point
        ob_expected = x * yg % p * pow(xg * y % p, -1, p) % p if x else 0
        if columns["OB"][i] != ob_expected:
            raise AssertionError("omega_b charged coordinate factorization failed")
        neutral = (
            row.cm_r * pow(rg, -1, p)
            * (anchor_row.cm_t + 7)
            * pow(row.cm_t + 7, -1, p)
        ) % p
        if columns["OA"][i] * columns["OB"][i] % p != neutral:
            raise AssertionError("charged-neutral moduli factorization failed")
        factorization_checks += 2

    quotient_tuples = list(zip(columns["T"], columns["R"], columns["S"]))
    if not tuple_mixed(quotient_tuples, rows):
        raise AssertionError("quotient state unexpectedly separates parity")

    scalar_status = {
        name: {
            "distinct": len(set(columns[name])),
            "mixed_parity_collisions": mixed_parity_collisions(columns[name], rows),
        }
        for name in SCALAR_STATES + ("R", "S", "T")
    }
    pair_status = {}
    for left, right in PAIR_STATES:
        values = list(zip(columns[left], columns[right]))
        pair_status[f"{left}|{right}"] = {
            "distinct": len(set(values)),
            "mixed_parity_collision": tuple_mixed(values, rows),
        }

    return {
        "negation_covariance_checks": neg_checks,
        "glv_weight_checks": glv_checks,
        "quotient_invariance_checks": quotient_checks,
        "charged_neutral_factorization_checks": factorization_checks,
        "quotient_state_has_exact_opposite_parity_collision": True,
        "glv_triple_collapses_to_one_quotient_state": True,
        "scalar_state_status": scalar_status,
        "pair_state_status": pair_status,
    }


class FpVectorBasis:
    def __init__(self, p: int):
        self.p = p
        self.rows: dict[int, list[int]] = {}

    def _reduce(self, vector: list[int]) -> list[int]:
        p = self.p
        v = vector[:]
        for pivot in sorted(self.rows):
            if v[pivot]:
                scale = v[pivot]
                row = self.rows[pivot]
                v = [(a - scale * b) % p for a, b in zip(v, row)]
        return v

    def add(self, vector: list[int]) -> bool:
        p = self.p
        v = self._reduce(vector)
        if not any(v):
            return False
        pivot = next(i for i, value in enumerate(v) if value)
        inv = pow(v[pivot], -1, p)
        v = [value * inv % p for value in v]
        for old_pivot, row in list(self.rows.items()):
            if row[pivot]:
                scale = row[pivot]
                self.rows[old_pivot] = [
                    (a - scale * b) % p for a, b in zip(row, v)
                ]
        self.rows[pivot] = v
        return True

    def contains(self, vector: list[int]) -> bool:
        return not any(self._reduce(vector))

    @property
    def rank(self) -> int:
        return len(self.rows)


def polynomial_degree_screen(
    rows: list[StateRow], context: dict[str, int], columns: dict[str, list[int]],
    max_degree: int = 12,
) -> dict[str, Any]:
    p = context["p"]
    target = [1 if row.k % 2 == 0 else p - 1 for row in rows]
    results = {}
    for left, right in PAIR_STATES[:2]:
        xs, ys = columns[left], columns[right]
        basis = FpVectorBasis(p)
        first_degree = None
        degree_rows = []
        monomial_count = 0
        for degree in range(max_degree + 1):
            for i in range(degree + 1):
                j = degree - i
                basis.add([
                    pow(x, i, p) * pow(y, j, p) % p
                    for x, y in zip(xs, ys)
                ])
                monomial_count += 1
            contained = basis.contains(target)
            degree_rows.append({
                "degree": degree,
                "monomials": monomial_count,
                "rank": basis.rank,
                "target_in_span": contained,
            })
            if contained and first_degree is None:
                first_degree = degree
        results[f"{left}|{right}"] = {
            "first_degree_at_most_bound": first_degree,
            "bound": max_degree,
            "degrees": degree_rows,
        }
    return results


def uniform_character_screen(curve_data: list[dict[str, Any]]) -> dict[str, Any]:
    target_signs: list[int] = []
    for data in curve_data:
        target_signs.extend(1 if row.k % 2 == 0 else -1 for row in data["rows"])
    target = bit_vector(target_signs)
    basis = XorBasis()
    declared = valid = 0
    exact_single = []

    monomial_specs = (
        ("U", 1), ("V", 1), ("V", 2), ("V", 3),
        ("UV", 1), ("U2V", 1), ("OA", 1), ("D", 1), ("P", 1),
    )
    for state_name, exponent in monomial_specs:
        for shift_name in structural_constants(curve_data[0]["context"]):
            declared += 1
            signs: list[int] = []
            good = True
            for data in curve_data:
                p = data["context"]["p"]
                shift = structural_constants(data["context"])[shift_name]
                for value in data["columns"][state_name]:
                    sign = quadratic_character(pow(value, exponent, p) + shift, p)
                    if sign == 0:
                        good = False
                        break
                    signs.append(sign)
                if not good:
                    break
            if not good:
                continue
            valid += 1
            vector = bit_vector(signs)
            basis.add(vector)
            if vector == target:
                exact_single.append({
                    "state": state_name, "exponent": exponent,
                    "shift": shift_name,
                })

    forms = (
        ("U", "V", "bilinear"),
        ("U", "V", "quadratic"),
        ("OA", "OB", "bilinear"),
        ("D", "OB", "bilinear"),
    )
    constant_names = tuple(structural_constants(curve_data[0]["context"]))
    alpha_names = ("one", "minus_one", "beta", "beta2", "lambda", "inv2", "inv3")
    for left, right, form in forms:
        for alpha_name in alpha_names:
            for shift_name in constant_names:
                declared += 1
                signs = []
                good = True
                for data in curve_data:
                    p = data["context"]["p"]
                    constants = structural_constants(data["context"])
                    alpha = constants[alpha_name]
                    shift = constants[shift_name]
                    for x, y in zip(data["columns"][left], data["columns"][right]):
                        if form == "bilinear":
                            value = x * y + alpha * x + y + shift
                        else:
                            value = x * x + alpha * x * y + y * y + shift
                        sign = quadratic_character(value, p)
                        if sign == 0:
                            good = False
                            break
                        signs.append(sign)
                    if not good:
                        break
                if not good:
                    continue
                valid += 1
                vector = bit_vector(signs)
                basis.add(vector)
                if vector == target:
                    exact_single.append({
                        "left": left, "right": right, "form": form,
                        "alpha": alpha_name, "shift": shift_name,
                    })

    return {
        "curves": len(curve_data),
        "rows": len(target_signs),
        "declared_atoms": declared,
        "valid_atoms": valid,
        "span_rank": basis.rank,
        "target_in_arbitrary_product_span": basis.contains(target),
        "exact_single_atoms": exact_single,
    }


def projective_tuples(p: int, dimension: int):
    """Canonical representatives of P^(dimension-1)(F_p)."""
    for first in range(dimension):
        prefix = [0] * first + [1]
        tail_length = dimension - first - 1
        if tail_length == 0:
            yield tuple(prefix)
            continue
        total = p**tail_length
        for encoded in range(total):
            tail = []
            value = encoded
            for _ in range(tail_length):
                tail.append(value % p)
                value //= p
            yield tuple(prefix + tail)


def complete_p43_nonlinear_screen(
    rows: list[StateRow], context: dict[str, int], columns: dict[str, list[int]]
) -> dict[str, Any]:
    p = context["p"]
    if p != 43:
        raise AssertionError("complete nonlinear screen is pinned to p=43")
    target = bit_vector([1 if row.k % 2 == 0 else -1 for row in rows])
    basis = XorBasis()
    declared = valid = 0
    survivors = []

    pair_forms = (
        ("U", "V", "bilinear"),
        ("U", "V", "quadratic"),
        ("OA", "OB", "bilinear"),
        ("OA", "OB", "quadratic"),
    )
    for left, right, kind in pair_forms:
        xs, ys = columns[left], columns[right]
        for coefficients in projective_tuples(p, 4):
            a, b, c, d = coefficients
            declared += 1
            if kind == "bilinear":
                values = [a*x*y + b*x + c*y + d for x, y in zip(xs, ys)]
            else:
                values = [a*x*x + b*x*y + c*y*y + d for x, y in zip(xs, ys)]
            signs = [quadratic_character(value, p) for value in values]
            if 0 in signs:
                continue
            valid += 1
            vector = bit_vector(signs)
            basis.add(vector)
            if vector == target:
                survivors.append({
                    "state": f"{left}|{right}", "kind": kind,
                    "coefficients": list(coefficients),
                })

    for state in ("V", "P", "UV"):
        values = columns[state]
        for coefficients in projective_tuples(p, 4):
            a, b, c, d = coefficients
            declared += 1
            signs = [
                quadratic_character(a*z**3 + b*z*z + c*z + d, p)
                for z in values
            ]
            if 0 in signs:
                continue
            valid += 1
            vector = bit_vector(signs)
            basis.add(vector)
            if vector == target:
                survivors.append({
                    "state": state, "kind": "cubic",
                    "coefficients": list(coefficients),
                })

    return {
        "p": p,
        "rows": len(rows),
        "declared_atoms": declared,
        "valid_atoms": valid,
        "span_rank": basis.rank,
        "target_in_arbitrary_product_span": basis.contains(target),
        "exact_single_survivors": survivors,
    }


def analyze_curve(row, label: str, degree_bound: int = 12) -> dict[str, Any]:
    rows, context = curve_rows(row)
    columns = charged_columns(rows, context)
    connection = connection_analysis(rows, context)
    covariance = covariance_analysis(rows, context, columns)
    polynomial = polynomial_degree_screen(rows, context, columns, degree_bound)
    return {
        "label": label,
        "p": context["p"],
        "n": context["n"],
        "rows": rows,
        "context": context,
        "columns": columns,
        "connection": connection,
        "covariance": covariance,
        "polynomial_decoder": polynomial,
        "errors": 0,
    }


def public_curve_result(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": data["label"],
        "p": data["p"],
        "n": data["n"],
        "rows": len(data["rows"]),
        "connection": data["connection"],
        "covariance": data["covariance"],
        "polynomial_decoder": data["polynomial_decoder"],
        "errors": data["errors"],
    }
