#!/usr/bin/env python3
"""Dickson recurrence and trace screens for UORC056 C20."""
from __future__ import annotations

from uorc056_negation_paired_core import *

def dickson_polynomials(max_index: int) -> list[dict[tuple[int, int], int]]:
    """U_j in Z[S,K], represented by {(S exponent,K exponent): coefficient}."""
    polys: list[dict[tuple[int, int], int]] = [{(0, 0): 2}, {(1, 0): 1}]
    for _j in range(2, max_index + 1):
        out: dict[tuple[int, int], int] = {}
        for (s_exp, k_exp), coeff in polys[-1].items():
            out[(s_exp + 1, k_exp)] = out.get((s_exp + 1, k_exp), 0) + coeff
        for (s_exp, k_exp), coeff in polys[-2].items():
            out[(s_exp, k_exp + 1)] = out.get((s_exp, k_exp + 1), 0) - coeff
        polys.append({key: value for key, value in out.items() if value})
    for j, poly in enumerate(polys):
        for (s_exp, k_exp), coeff in poly.items():
            if coeff == 0 or s_exp + 2 * k_exp != j or s_exp % 2 != j % 2:
                raise AssertionError("Dickson homogeneity/parity certificate failed")
    return polys

def dickson_symbolic_certificate() -> dict[str, object]:
    polys = dickson_polynomials(max(DICKSON_ODD_INDICES))
    selected = {}
    for j in DICKSON_ODD_INDICES:
        poly = polys[j]
        if not all(s_exp & 1 for s_exp, _ in poly):
            raise AssertionError("odd Dickson polynomial lacks the S factor")
        selected[str(j)] = {
            "terms": len(poly),
            "branch_parity": "odd",
            "has_mandatory_S_factor": True,
            "coefficient_l1": sum(abs(value) for value in poly.values()),
        }
    return {
        "recurrence": "U_0=2; U_1=S; U_j=S*U_(j-1)-K*U_(j-2)",
        "even_form": "U_(2r) in F[S^2,K]",
        "odd_form": "U_(2r+1)=S*V_r(S^2,K)",
        "selected_indices": selected,
        "short_index_recurrence_does_not_construct_S": True,
    }

def _ls(C, r, point, p: int):
    return c19.ls_from_dict(
        C.series_laurent(r, point, K=LOCAL_SERIES_TERMS),
        p,
        LOCAL_SERIES_TERMS,
    )

def dickson_trace_screen(C, points, Z, Zneg, endpoint: list[int], lam: int) -> dict[str, object]:
    p = C.p
    n = len(points)
    conjugates = [Z, C.rf_phi(Z), C.rf_phi(C.rf_phi(Z))]
    neg_conjugates = [Zneg, C.rf_phi(Zneg), C.rf_phi(C.rf_phi(Zneg))]
    parity = [1 if k % 2 == 0 else -1 for k in range(n)]
    correction = {k for k in range(1, n) if endpoint[k] != parity[k]}
    rows = c19.orbit_rows(n, lam, correction)
    metrics = {
        j: {"quotient_support": 0, "quotient_pole_degree": 0,
            "uncertain_orbits": 0, "valuation_histogram": {}}
        for j in DICKSON_ODD_INDICES
    }
    for row in rows:
        point = points[row["representative"]]
        z_series = [_ls(C, r, point, p) for r in conjugates]
        zn_series = [_ls(C, r, point, p) for r in neg_conjugates]
        if any(series is None for series in z_series + zn_series):
            raise AssertionError("paired endpoint series vanished to truncation")
        for j in DICKSON_ODD_INDICES:
            total = None
            for z, zn in zip(z_series, zn_series):
                term = c19.ls_add(
                    c19.ls_pow(z, j, p, LOCAL_SERIES_TERMS),
                    c19.ls_pow(zn, j, p, LOCAL_SERIES_TERMS),
                    p,
                    LOCAL_SERIES_TERMS,
                )
                total = c19.ls_add(total, term, p, LOCAL_SERIES_TERMS)
            metric = metrics[j]
            if total is None:
                metric["uncertain_orbits"] += 1
                continue
            valuation = total.v
            metric["quotient_support"] += int(valuation != 0)
            metric["quotient_pole_degree"] += max(-valuation, 0)
            key = str(valuation)
            metric["valuation_histogram"][key] = metric["valuation_histogram"].get(key, 0) + 1
    return {
        "indices": list(DICKSON_ODD_INDICES),
        "quotient_orbits": len(rows),
        "metrics": {str(j): metrics[j] for j in DICKSON_ODD_INDICES},
        "all_screened_traces_have_full_quotient_support": all(
            metrics[j]["quotient_support"] == len(rows)
            and metrics[j]["uncertain_orbits"] == 0
            for j in DICKSON_ODD_INDICES
        ),
    }
