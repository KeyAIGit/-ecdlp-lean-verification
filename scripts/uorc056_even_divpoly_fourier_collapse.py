#!/usr/bin/env python3
"""UORC-056 even division-polynomial Fourier collapse V10.

For an odd cyclic subgroup H=<G> of order n and an exact evaluator based on a
single division polynomial, this package proves:

* odd indices fail negation covariance;
* for m=2u with gcd(u,n)=1, the chain rule gives

      chi(psi_m(Q)) = chi(psi_2([u]Q));

* a near-half Fourier coefficient of parity has magnitude cot(pi/(2n));
* Shparlinski-Stange Lemma 5 bounds every subgroup Fourier coefficient of
  chi(psi_2) by 6*sqrt(q), because the rational map psi_2=2y has degree three;
* the sharper odd-support conductor calculation gives 4*sqrt(q), but that
  refinement remains part of the provisional V8 sheaf package.

Hence no pure division-polynomial character can equal canonical parity whenever
cot(pi/(2n)) > 6*sqrt(q). The published bound closes secp256k1 independently of
V8. Four small frozen curves outside that inequality are closed by exhaustive
scanning of every multiplier class u modulo n.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

import uorc056_division_polynomial_frontier as v9

PROFILE_ID = "UORC-056-EVEN-DIVPOLY-FOURIER-COLLAPSE-V10"
SECP256K1_P = v9.SECP256K1_P
SECP256K1_N = v9.SECP256K1_N
Curve = v9.Curve


def stable_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def parity_peak(n: int) -> float:
    if n < 3 or n % 2 == 0:
        raise ValueError("n must be odd and at least three")
    return 1.0 / math.tan(math.pi / (2.0 * n))


def certified_cot_lower_fraction(n: int) -> tuple[int, int]:
    if n < 3 or n % 2 == 0:
        raise ValueError("n must be odd and at least three")
    return 98 * n * n - 121, 154 * n


def certified_peak_exceeds_constant_sqrt(
    q: int,
    n: int,
    constant: int,
) -> bool:
    if constant <= 0:
        raise ValueError("constant must be positive")
    numerator, denominator = certified_cot_lower_fraction(n)
    return (
        numerator * numerator
        > constant * constant * denominator * denominator * q
    )


def certified_peak_exceeds_four_sqrt(q: int, n: int) -> bool:
    return certified_peak_exceeds_constant_sqrt(q, n, 4)


def certified_peak_exceeds_six_sqrt(q: int, n: int) -> bool:
    return certified_peak_exceeds_constant_sqrt(q, n, 6)


def parse_corpora(grammar_path: Path) -> tuple[Curve, ...]:
    grammar = json.loads(grammar_path.read_text(encoding="utf-8"))
    rows = grammar["discovery_corpus"] + grammar["holdout_corpus"]
    return tuple(v9.parse_curve(row) for row in rows)


def psi_two_character_table(curve: Curve) -> list[int]:
    prime, order, generator = curve
    table = [0] * order
    for scalar in range(1, order):
        point = v9.ec_mul(scalar, generator, prime)
        if point is None:
            raise AssertionError("nonzero subgroup point became identity")
        value = (2 * point[1]) % prime
        sign = v9.quadratic_character(value, prime)
        if sign == 0:
            raise AssertionError("odd-order subgroup met 2-torsion")
        table[scalar] = sign
    return table


def exhaustive_multiplier_scan(curve: Curve) -> dict[str, Any]:
    prime, order, _ = curve
    table = psi_two_character_table(curve)
    candidates: list[dict[str, int]] = []
    best = {"matches": -1, "u": None, "output_phase": None}
    for multiplier in range(1, order):
        if math.gcd(multiplier, order) != 1:
            continue
        direct = 0
        for scalar in range(1, order):
            value = table[(multiplier * scalar) % order]
            target = -1 if scalar & 1 else 1
            direct += int(value == target)
        for phase, matches in ((1, direct), (-1, order - 1 - direct)):
            if matches > best["matches"]:
                best = {
                    "matches": matches,
                    "u": multiplier,
                    "output_phase": phase,
                }
            if matches == order - 1:
                candidates.append({"u": multiplier, "output_phase": phase})

    published_closed = certified_peak_exceeds_six_sqrt(prime, order)
    sharp_closed = certified_peak_exceeds_four_sqrt(prime, order)
    return {
        "p": prime,
        "n": order,
        "multiplier_classes_tested": sum(
            math.gcd(multiplier, order) == 1
            for multiplier in range(1, order)
        ),
        "exact_candidates": candidates,
        "best": {
            **best,
            "total": order - 1,
            "accuracy": f"{best['matches'] / (order - 1):.9f}",
        },
        "parity_peak": f"{parity_peak(order):.15e}",
        "four_sqrt_q": f"{4.0 * math.sqrt(prime):.15e}",
        "six_sqrt_q": f"{6.0 * math.sqrt(prime):.15e}",
        "certified_sharp_fourier_closed": sharp_closed,
        "certified_published_fourier_closed": published_closed,
        "closure_basis": (
            "published_6sqrt_bound"
            if published_closed
            else "complete_multiplier_scan"
        ),
    }


def verify_chain_collapse(
    curves: Iterable[Curve],
    maximum_even_index: int = 256,
) -> dict[str, int]:
    checks = 0
    for prime, order, generator in curves:
        maximum = min(maximum_even_index, 4 * order)
        for scalar in range(1, order):
            point = v9.ec_mul(scalar, generator, prime)
            if point is None:
                raise AssertionError("unexpected identity")
            evaluator = v9.DivisionPolynomialEvaluator(prime, 0, 7, point)
            for index in range(2, maximum + 1, 2):
                half = index // 2
                if math.gcd(half, order) != 1:
                    continue
                direct = v9.quadratic_character(
                    evaluator.value(index), prime
                )
                image = v9.ec_mul(half, point, prime)
                if image is None:
                    raise AssertionError("invertible multiplier hit identity")
                collapsed = v9.quadratic_character(2 * image[1], prime)
                if direct != collapsed:
                    raise AssertionError(
                        f"chain collapse failed p={prime}, k={scalar}, m={index}"
                    )
                checks += 1
    return {
        "maximum_even_index": maximum_even_index,
        "point_index_checks": checks,
    }


def secp_record() -> dict[str, Any]:
    numerator, denominator = certified_cot_lower_fraction(SECP256K1_N)
    published_closed = certified_peak_exceeds_six_sqrt(
        SECP256K1_P,
        SECP256K1_N,
    )
    sharp_closed = certified_peak_exceeds_four_sqrt(
        SECP256K1_P,
        SECP256K1_N,
    )
    if not published_closed or not sharp_closed:
        raise AssertionError("secp256k1 Fourier closure unexpectedly failed")

    ratio_six = parity_peak(SECP256K1_N) / (
        6.0 * math.sqrt(SECP256K1_P)
    )
    ratio_four = parity_peak(SECP256K1_N) / (
        4.0 * math.sqrt(SECP256K1_P)
    )
    return {
        "p": str(SECP256K1_P),
        "n": str(SECP256K1_N),
        "certified_cot_lower_numerator": str(numerator),
        "certified_cot_lower_denominator": str(denominator),
        "certified_published_inequality": (
            "(98*n^2-121)^2 > 36*(154*n)^2*p"
        ),
        "certified_published_six_sqrt_closed": published_closed,
        "peak_over_six_sqrt_p": f"{ratio_six:.15e}",
        "peak_over_six_sqrt_p_log2": f"{math.log2(ratio_six):.12f}",
        "certified_sharp_inequality": (
            "(98*n^2-121)^2 > 16*(154*n)^2*p"
        ),
        "certified_sharp_four_sqrt_closed": sharp_closed,
        "peak_over_four_sqrt_p": f"{ratio_four:.15e}",
        "peak_over_four_sqrt_p_log2": f"{math.log2(ratio_four):.12f}",
        "decision": (
            "no chi(psi_m(Q)) with any positive integer m can equal "
            "canonical parity on all nonzero secp256k1 subgroup points"
        ),
    }


def run(grammar_path: Path) -> dict[str, Any]:
    curves = parse_corpora(grammar_path)
    scans = [exhaustive_multiplier_scan(curve) for curve in curves]
    if any(row["exact_candidates"] for row in scans):
        raise AssertionError("unexpected exact psi_2 multiplier candidate")
    chain_replay = verify_chain_collapse(curves[:5])

    published_closed = sum(
        row["certified_published_fourier_closed"] for row in scans
    )
    sharp_closed = sum(
        row["certified_sharp_fourier_closed"] for row in scans
    )

    grammar_bytes = grammar_path.read_bytes()
    return {
        "schema_version": "1.1",
        "experiment": PROFILE_ID,
        "review_status": (
            "the chain-rule reduction, complete multiplier scans, exact integer "
            "certificates and the published 6*sqrt(q) subgroup-character estimate "
            "are independently reproducible; the sharper 4*sqrt(q) sheaf-conductor "
            "refinement remains subject to specialist review"
        ),
        "input_grammar_sha256": hashlib.sha256(grammar_bytes).hexdigest(),
        "theorem": {
            "odd_index_closure": (
                "psi_m(-Q)=psi_m(Q) for odd m, while canonical parity is "
                "anti-invariant"
            ),
            "even_chain_collapse": (
                "for m=2u, psi_m=(psi_2 o [u])*psi_u^4, so "
                "chi(psi_m(Q))=chi(psi_2([u]Q)) whenever gcd(u,n)=1"
            ),
            "peak_identity": (
                "canonical parity has a subgroup Fourier coefficient of "
                "magnitude cot(pi/(2n))"
            ),
            "published_base_trace_bound": (
                "Shparlinski-Stange Lemma 5 gives every subgroup Fourier "
                "coefficient of chi(psi_2) magnitude at most 6*sqrt(q), "
                "because deg(psi_2)=3"
            ),
            "published_necessary_condition": (
                "cot(pi/(2n)) <= 6*sqrt(q)"
            ),
            "sharp_base_trace_bound": (
                "the odd-support conductor calculation gives the sharper "
                "provisional bound 4*sqrt(q)"
            ),
            "sharp_necessary_condition": (
                "cot(pi/(2n)) <= 4*sqrt(q)"
            ),
            "support_reason": (
                "div(psi_2)=sum_{T in E[2] minus {O}}[T]-3[O], so the "
                "geometric odd support has size four and psi_2 is not a square"
            ),
        },
        "corpus": {
            "curve_count": len(scans),
            "curves_closed_by_published_six_sqrt_inequality": published_closed,
            "curves_requiring_complete_multiplier_scan_under_published_bound": (
                len(scans) - published_closed
            ),
            "curves_closed_by_sharp_four_sqrt_inequality": sharp_closed,
            "curves_requiring_complete_multiplier_scan_under_sharp_bound": (
                len(scans) - sharp_closed
            ),
            "all_multiplier_scans_exact_negative": True,
            "records": scans,
        },
        "chain_rule_replay": chain_replay,
        "secp256k1": secp_record(),
        "decision": (
            "the pure single-division-polynomial character route is closed "
            "for secp256k1 by the published 6*sqrt(q) theorem and for every "
            "curve in the frozen eighteen-curve corpus by that theorem plus "
            "complete multiplier scans"
        ),
        "independent_cross_check": (
            "the q=3 mod 4 secp256k1 case is also closed by the elementary "
            "Paley tournament obstruction in "
            "UORC056_EDS_PALEY_OBSTRUCTION_V10"
        ),
        "supersedes": (
            "the V9 open even-index q=3 mod 4 EDS-decimation case for pure "
            "single division-polynomial characters"
        ),
        "remaining_scope": [
            "products of multiple independently pulled division-polynomial characters",
            "direct field-valued Y_G evaluation without one outer quadratic character",
            "theta or elliptic-unit evaluators",
            "adaptive branching and non-character outputs",
        ],
        "claim_boundary": [
            "The theorem closes one pure character chi(psi_m(Q)) with an optional global phase.",
            "The published 6*sqrt(q) estimate is enough for secp256k1; the sharper 4*sqrt(q) estimate remains a provisional refinement.",
            "Finite multiplier scans are complete only for the declared eighteen toy curves.",
            "No external point, wallet, real key or unknown production scalar is used.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--grammar",
        type=Path,
        default=Path(
            "experiments/uorc056/divisor_aware_rational_grammar.json"
        ),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(
            "experiments/uorc056/even_divpoly_fourier_collapse_results.json"
        ),
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = stable_json(run(args.grammar))
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("even division-polynomial Fourier result drift")
        print("UORC056_EVEN_DIVPOLY_FOURIER_COLLAPSE_OK")
        return 0
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
